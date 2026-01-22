import fnmatch
import glob
import os
import shutil

import spack.cmd
import spack.config
import spack.environment
import spack.extensions
import spack.llnl.util.filesystem as fs
import spack.llnl.util.tty as tty
import spack.spec
import spack.util.path
import spack.util.spack_yaml
from spack.cmd.mirror import create_mirror_for_all_specs, filter_externals
from spack.main import SpackCommand
from spack.paths import spack_root

description = "bundle an environment as a self-contained source distribution"
section = "manager"
level = "long"


SPACK_USER_PATTERNS = ["var/*", "opt/*", ".git*", "etc/spack/*"]
CONFIG_SECTION_EXCLUDES = ["mirrors", "repos", "include"]


def add_command(parser, command_dict):
    subparser = parser.add_parser("distribution", help=description)
    subparser.add_argument(
        "--distro-dir",
        default=os.path.join(os.getcwd(), "distro"),
        help="Directory where the packaged environment should be created",
    )
    subparser.add_argument(
        "--include", help="Directory containing yaml to be included in the packaged environment"
    )

    subparser.add_argument(
        "--exclude",
        help="Directory containing yaml to be explicitly removed from packaged environment",
    )
    subparser.add_argument(
        "--filter-externals",
        action="store_true",
        help=(
            "Remove any package settings that declare a path to an external "
            "installation of the package's binaries"
        ),
    )
    subparser.add_argument(
        "--extra-data",
        help=(
            "Directory where any additional data to be copied "
            "into the root of the packaged distribution"
        ),
    )
    subparser.add_argument(
        "--exclude-config-section",
        default="",
        help=(
            "Explicitly exclude this section in the new config file (i.e. 'aliases', 'env_vars')"
        ),
    )
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "--source-only",
        action="store_true",
        help=(
            "Only create a source mirror for packages in the environment. "
            "Default is to create a source and binary mirror"
        ),
    )
    group.add_argument(
        "--binary-only",
        action="store_true",
        help=(
            "Only create a binary mirror for packages in the environment. "
            "Default is to create a source and binary mirror"
        ),
    )
    command_dict["distribution"] = distribution


def _read_config(filename):
    return spack.config.read_config_file(filename)


def get_env_as_dict(env):
    return _read_config(os.path.join(env.path, "spack.yaml"))


def get_local_config(path):
    little_config = {}
    for f in os.listdir(path):
        little_config.update(_read_config(os.path.join(path, f)))
    return little_config


def is_match(string, patterns):
    return any(fnmatch.fnmatch(string, pattern) for pattern in patterns)


def copy_files_excluding_pattern(src, dst, patterns):
    os.makedirs(dst, exist_ok=True)

    for dirpath, _, filenames in os.walk(src):
        relative_path = os.path.relpath(dirpath, src)
        dst_dir = os.path.join(dst, relative_path)
        if not is_match(relative_path, patterns):
            os.makedirs(dst_dir, exist_ok=True)

            for filename in filenames:
                src_file = os.path.join(dirpath, filename)
                dst_file = os.path.join(dst_dir, filename)

                if not is_match(os.path.join(relative_path, filename), patterns):
                    shutil.copy2(src_file, dst_file, follow_symlinks=False)


def remove_subset_from_dict(larger_dict, subset_dict):
    """
    Removes the subset dictionary from the larger dictionary, including items in lists,
    and deletes keys if the subset value is an empty dictionary.

    :param larger_dict: The larger dictionary from which the subset will be removed.
    :param subset_dict: The subset dictionary to remove.
    :return: The modified larger dictionary.
    """
    for key, value in subset_dict.items():
        if key in larger_dict:
            if not value:
                del larger_dict[key]
            elif isinstance(value, dict) and isinstance(larger_dict[key], dict):
                remove_subset_from_dict(larger_dict[key], value)
                if not larger_dict[key]:
                    del larger_dict[key]
            elif isinstance(value, list) and isinstance(larger_dict[key], list):
                larger_dict[key] = [item for item in larger_dict[key] if item not in value]
                if not larger_dict[key]:
                    del larger_dict[key]
            elif larger_dict[key] == value:
                del larger_dict[key]
    return larger_dict


def valid_env_scopes(env):
    scopes = spack.config.CONFIG.matching_scopes(f"^env:{env.name}|^include:")
    return [s.name for s in scopes]


def bundle_spack(location):
    tty.msg(f"Packing up Spack installation to {location}....")
    copy_files_excluding_pattern(spack_root, location, SPACK_USER_PATTERNS)


class DistributionPackager:
    def __init__(self, env, root, includes=None, excludes=None, extra_data=None):
        self.environment_to_package = env
        self.includes = includes
        self.excludes = excludes
        self.extra_data = extra_data

        self.path = root
        self.package_repos = os.path.join(self.path, "spack_repo")
        self.extensions = os.path.join(self.path, "extensions")
        self.source_mirror = os.path.join(self.path, "source-mirror")
        self.binary_mirror = os.path.join(self.path, "binary-mirror")
        self.bootstrap_mirror = os.path.join(self.path, "bootstrap-mirror")
        self.spack_dir = os.path.join(self.path, "spack")

        self._env = None
        self._cached_env = None
        self._flattened_config  = {}

    def __enter__(self):
        self._cached_env = spack.environment.active_environment()
        tty.msg(f"Concretizing env: {self.environment_to_package.name}....")
        self.environment_to_package.concretize()
        self.environment_to_package.write()
        spack.environment.deactivate()
        self.init_distro_dir()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.filter_excludes()
        self.remove_unwanted_artifacts()
        if self._cached_env:
            spack.environment.activate(self._cached_env)

    @property
    def env(self):
        if self._env is None:
            epath = os.path.join(self.path, "environment")
            self._env = spack.environment.create_in_dir(epath, keep_relative=True)
        return self._env

    def init_distro_dir(self):
        tty.msg("Precleaning....")
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)
        os.makedirs(self.path)

    def filter_excludes(self):
        tty.msg(f"Writing manifest file for env: {self.env.name}....")
        env_data = get_env_as_dict(self.env)
        if self.excludes:
            tty.msg(f"Processing settings to exclude from env: {self.env.name}....")
            cfg = get_local_config(self.excludes)
            remove_subset_from_dict(env_data["spack"], cfg)
        self._write(env_data)

    def concretize(self):
        tty.msg(f"Concretizing env: {self.env.name}....")
        self.env.concretize(force=True)
        self.env.write()

    def remove_unwanted_artifacts(self):
        for pattern in SPACK_USER_PATTERNS:
            remove_by_pattern(os.path.join(self.spack_dir, pattern))
        for item in os.listdir(self.env.path):
            fullname = os.path.join(self.env.path, item)
            if "spack.yaml" in item:
                continue
            elif os.path.isdir(fullname):
                shutil.rmtree(fullname)
            else:
                os.remove(fullname)

    def get_flattened_config(self, config_excludes):
        with self.environment_to_package:
            for section in spack.config.SECTION_SCHEMAS:
                # Exclude sections of the config file we do not want
                if section in CONFIG_SECTION_EXCLUDES or section in config_excludes:
                    continue
                # We will set the extensions in the config later in the process
                elif section == "config":
                    self._flattened_config[section] = spack.config.CONFIG.get(section)
                    del self._flattened_config[section]['extensions']
                else:
                    self._flattened_config[section] = spack.config.CONFIG.get(section)

    def create_config(self):
        with self.env:
            for section in self._flattened_config:
                if self._flattened_config[section]:
                    spack.config.CONFIG.set(section, self._flattened_config[section], scope=self.env.scope_name)

    def configure_includes(self):
        if self.includes:
            tty.msg(f"Adding include dir to env: {self.env.name}....")
            includes_install = os.path.join(self.path, os.path.basename(self.includes))
            shutil.copytree(self.includes, includes_install)
            includes = os.path.relpath(includes_install, self.env.path)
            sconfig = SpackCommand("config")
            with self.env:
                with self.env.write_transaction():
                    sconfig("add", f"include:[{includes}]")

    def configure_specs(self):
        with self.environment_to_package:
            specs = self.environment_to_package.user_specs.specs_as_yaml_list

        adder = SpackCommand("add")
        tty.msg(f"Adding specs to env: {self.env.name}....")
        with self.env:
            for spec in specs:
                with self.env.write_transaction():
                    adder(spec)

    def configure_extensions(self):
        with self.environment_to_package:
            extensions = spack.extensions.get_extension_paths()
            tty.msg(f"Packing up extensions to {self.extensions}....")
            os.makedirs(self.extensions)
            for extension in extensions:
                shutil.copytree(
                    extension,
                    os.path.join(self.extensions, os.path.basename(extension)),
                    ignore=shutil.ignore_patterns(".git*", "spack"),
                )

        tty.msg(f"Packaging up extensions to env: {self.env.name}....")
        sconfig = SpackCommand("config")
        with self.env:
            for extension in extensions:
                extension = os.path.join(
                    os.path.relpath(self.extensions, self.env.path), os.path.basename(extension)
                )
                with self.env.write_transaction():
                    sconfig("add", f"config:extensions:[{extension}]")

    def configure_package_repos(self):
        with self.environment_to_package:
            repos = spack.util.spack_yaml.syaml_dict()
            for scope in valid_env_scopes(self.environment_to_package):
                repos.update(spack.config.get("repos", scope=scope))

        tty.msg(f"Packing up package repositories to {self.package_repos}....")
        os.makedirs(self.package_repos)

        for name, repo in repos.items():
            repo = spack.util.path.canonicalize_path(repo)
            basename = os.path.basename(repo)
            repos[name] = os.path.join(
                os.path.relpath(self.package_repos, self.env.path), basename
            )
            shutil.copytree(repo, os.path.join(self.package_repos, basename))

        tty.msg(f"Adding repositories to env: {self.env.name}....")
        env = get_env_as_dict(self.env)
        env["spack"]["repos"] = repos
        self._write(env)

    def configure_package_settings(self, filter_externals=False):
        tty.msg(f"Add package settings to env: {self.env.name}....")
        with self.environment_to_package:
            package_settings = {}
            for scope in valid_env_scopes(self.environment_to_package):
                for package, data in spack.config.get("packages", scope=scope).items():
                    if "externals" not in data or not filter_externals:
                        try:
                            package_settings[package].update(data)
                        except KeyError:
                            package_settings[package] = data

        env_data = get_env_as_dict(self.env)
        env_data["spack"]["packages"] = package_settings
        self._write(env_data)

    def configure_source_mirror(self):
        # We do not want to omit any packages that are externals
        # just So They Build Faster internally, but are still needed externally.
        # However, this causes issues for packages that are not downloadable,
        # so we do a first-shot mirror creation with the original environment active.
        with self.environment_to_package:
            tty.msg(f"Creating source mirror at {self.source_mirror}....")
            create_mirror_for_all_specs(
                mirror_specs=filter_externals(self.environment_to_package.all_specs()),
                path=self.source_mirror,
                skip_unstable_versions=False,
                workers=spack.config.determine_number_of_jobs(parallel=True),
            )

        with self.env:
            tty.msg(f"Updating mirror at {self.source_mirror}....")
            create_mirror_for_all_specs(
                mirror_specs=filter_externals(self.env.all_specs()),
                path=self.source_mirror,
                skip_unstable_versions=False,
                workers=spack.config.determine_number_of_jobs(parallel=True),
            )
            mirror_path = os.path.join(
                os.path.relpath(self.path, self.env.path), os.path.basename(self.source_mirror)
            )

            mirrorer = SpackCommand("mirror")
            tty.msg(f"Adding mirror to env: {self.env.name}....")
            with self.env.write_transaction():
                mirrorer("add", "internal-source", mirror_path)

    def configure_binary_mirror(self):
        cacher = SpackCommand("buildcache")
        with self.environment_to_package:
            tty.msg(f"Creating binary mirror at {self.binary_mirror}....")
            cacher("push", "--unsigned", self.binary_mirror)
            cacher("keys", "--install", "--trust")

        mirrorer = SpackCommand("mirror")
        mirror_path = os.path.join(
            os.path.relpath(self.path, self.env.path), os.path.basename(self.binary_mirror)
        )
        mirror_name = "internal-binary"

        with self.env:
            tty.msg(f"Adding mirror to env: {self.env.name}....")
            with self.env.write_transaction():
                mirrorer("add", "--type", "binary", "--unsigned", mirror_name, mirror_path)

    def configure_bootstrap_mirror(self):
        tty.msg(f"Creating bootstrap mirror at {self.bootstrap_mirror}....")
        strapper = SpackCommand("bootstrap")
        strapper("mirror", "--binary-packages", self.bootstrap_mirror)
        bootstrap_source = os.path.join(
            os.path.relpath(self.bootstrap_mirror, self.env.path), "metadata", "sources"
        )
        bootstrap_binary = os.path.join(
            os.path.relpath(self.bootstrap_mirror, self.env.path), "metadata", "binaries"
        )
        with self.env:
            with fs.working_dir(self.env.path):
                with self.env.write_transaction():
                    strapper(
                        "add",
                        "--trust",
                        "--scope",
                        f"env:{self.env.name}",
                        "internal-sources",
                        bootstrap_source,
                    )
                with self.env.write_transaction():
                    strapper(
                        "add",
                        "--trust",
                        "--scope",
                        f"env:{self.env.name}",
                        "internal-binaries",
                        bootstrap_binary,
                    )

    def bundle_spack(self):
        os.makedirs(self.path, exist_ok=True)
        spack_install = os.path.join(self.path, "spack")
        tty.msg(f"Packing up Spack installation to {spack_install}....")
        ignore_these = ["var/spack/environments/*", "opt/*", ".git*", "etc/spack/include.yaml"]
        copy_files_excluding_pattern(spack_root, spack_install, ignore_these)

    def bundle_extra_data(self):
        if self.extra_data:
            os.makedirs(self.path, exist_ok=True)
            tty.msg(f"Packaging up extra data to {self.path}....")
            shutil.copytree(self.extra_data, self.path)

    def _write(self, data):
        with open(os.path.join(self.env.path, "spack.yaml"), "w") as outf:
            spack.util.spack_yaml.dump(data, outf, default_flow_style=False)


def is_installed(spec):
    deps = list(spec.dependencies(deptype=("link", "run")))
    bad_statuses = [spack.spec.InstallStatus.absent, spack.spec.InstallStatus.missing]
    dep_status = [x.install_status() not in bad_statuses for x in deps]
    return all(dep_status) and spec.install_status() not in bad_statuses


def correct_mirror_args(env, args):
    specs_to_check = list(env.concretized_specs())
    install_status = [len(specs_to_check)] + [is_installed(x) for _, x in specs_to_check]
    has_installed_specs = all(install_status)
    if not args.source_only and not has_installed_specs:
        tty.warn("Environment contains uninstalled specs, defaulting to source-only package")
        if args.binary_only:
            tty.die(
                "Binary distribution requested, but the environment does not "
                "include the necessary installed binary packages"
            )
        args.source_only = True


def remove_by_pattern(pattern):
    for item in glob.glob(pattern, recursive=True):
        tty.msg(item)
        if os.path.isfile(item):
            os.remove(item)
        elif os.path.isdir(item):
            shutil.rmtree(item)


def distribution(parser, args):
    env = spack.cmd.require_active_env(cmd_name="manager distribution")
    correct_mirror_args(env, args)

    packager = DistributionPackager(
        env,
        args.distro_dir,
        includes=args.include,
        excludes=args.exclude,
        extra_data=args.extra_data,
    )

    with packager:
        packager.get_flattened_config(config_excludes=args.exclude_config_section)
        packager.create_config()
        packager.configure_includes()
        packager.configure_specs()
        packager.configure_extensions()
        packager.configure_package_repos()
        packager.configure_package_settings(filter_externals=args.filter_externals)
        packager.filter_excludes()
        packager.concretize()
        if not args.binary_only:
            packager.configure_source_mirror()
        if not args.source_only:
            packager.configure_binary_mirror()
        packager.configure_bootstrap_mirror()
        packager.bundle_spack()
        packager.bundle_extra_data()
