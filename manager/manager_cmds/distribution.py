import fnmatch
import os
import shutil

import spack.cmd
import spack.config
import spack.extensions
import spack.llnl.util.tty as tty
import spack.util.path
import spack.util.spack_yaml
from spack import environment
from spack.cmd.mirror import create_mirror_for_all_specs, filter_externals
from spack.llnl.util.filesystem import working_dir
from spack.main import SpackCommand
from spack.paths import spack_root

description = "bundle an environment as a self-contained source distribution"
section = "manager"
level = "long"


def add_command(parser, command_dict):
    subparser = parser.add_parser("distribution", help=description)
    subparser.add_argument(
        "--distro-dir",
        default=os.path.join(os.getcwd(), "distro"),
        help="Directory where the packaged environemnt should be created",
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
            "Directory where any aditional data to be copied "
            "into the root of the packaged distribution"
        ),
    )
    command_dict["distribution"] = distribution


def get_env_as_dict(env):
    with env:
        data = spack.config.CONFIG.scopes[f"env:{env.name}"].sections
    env_data = {"spack": {}}
    for item in data.values():
        for k, v in item.items():
            env_data["spack"][k] = v
    return env_data


def get_local_config(name, path):
    sections = list(spack.config.SECTION_SCHEMAS.keys())
    scope = spack.config.DirectoryConfigScope(name, os.path.abspath(path))

    little_config = {}
    for section in sections:
        if scope.get_section(section):
            little_config.update(scope.get_section(section))
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
                    shutil.copy2(src_file, dst_file)


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
                # Recursively remove nested dictionaries
                remove_subset_from_dict(larger_dict[key], value)
                # If the nested dictionary becomes empty, remove the key
                if not larger_dict[key]:
                    del larger_dict[key]
            elif isinstance(value, list) and isinstance(larger_dict[key], list):
                # Remove matching items from the list
                larger_dict[key] = [item for item in larger_dict[key] if item not in value]
                # If the list becomes empty, remove the key
                if not larger_dict[key]:
                    del larger_dict[key]
            elif larger_dict[key] == value:
                # Remove the key if the value matches
                del larger_dict[key]
    return larger_dict


def valid_env_scopes(env):
    scopes = spack.config.CONFIG.matching_scopes(f"^env:{env.name}|^include:")
    return [s.name for s in scopes]


def bundle_spack(location):
    tty.msg(f"Packing up Spack installation to {location}....")
    ignore_these = ["var/spack/environments/*", "opt/*", ".git*", "etc/spack/include.yaml"]
    copy_files_excluding_pattern(spack_root, location, ignore_these)


class DistributionPackager:
    def __init__(self, env, root, includes=None, excludes=None, extra_data=None):
        self.orig = env
        self.includes = includes
        self.excludes = excludes
        self.extra_data = extra_data

        self.path = root
        self.package_repos = os.path.join(self.path, "spack_repo")
        self.extensions = os.path.join(self.path, "extensions")
        self.mirror = os.path.join(self.path, "mirror")
        self.bootstrap_mirror = os.path.join(self.path, "bootstrap-mirror")
        self.spack_dir = os.path.join(self.path, "spack")

        self._env = None
        self._cached_env = None

    @property
    def env(self):
        if self._env is None:
            epath = os.path.join(self.path, "environment")
            self._env = environment.create_in_dir(epath, keep_relative=True)
        return self._env

    def wipe_n_make(self):
        tty.msg("Precleaning....")
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)
        os.makedirs(self.path)

    def filter_excludes(self):
        tty.msg(f"Writing manifest file for env: {self.env.name}....")
        env_data = get_env_as_dict(self.env)
        if self.excludes:
            tty.msg(f"Processing settings to exclude from env: {self.env.name}....")
            cfg = get_local_config("exclude", self.excludes)
            remove_subset_from_dict(env_data["spack"], cfg)
        self._write(env_data)

    def filter_excludes_and_concretize(self):
        self.filter_excludes()
        tty.msg(f"Concretizing env: {self.env.name}....")
        self.env.concretize(force=True)
        self.env.write()

    def clean(self):
        for item in os.listdir(self.env.path):
            fullname = os.path.join(self.env.path, item)
            if "spack.yaml" in item:
                continue
            elif os.path.isdir(fullname):
                shutil.rmtree(fullname)
            else:
                os.remove(fullname)

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
        with self.orig:
            specs = self.orig.user_specs.specs_as_yaml_list

        adder = SpackCommand("add")
        tty.msg(f"Adding specs to env: {self.env.name}....")
        with self.env:
            for spec in specs:
                with self.env.write_transaction():
                    adder(spec)

    def configure_extensions(self):
        with self.orig:
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
        repos = set()
        with self.orig:
            for scope in valid_env_scopes(self.orig):
                for repo in spack.config.get("repos", scope=scope).values():
                    repos.add(spack.util.path.canonicalize_path(repo))

        tty.msg(f"Packing up package repositories to {self.package_repos}....")
        os.makedirs(self.package_repos)

        to_write = {}
        for repo in repos:
            name = os.path.basename(repo)
            to_write[name] = os.path.join(os.path.relpath(self.package_repos, self.env.path), name)
            shutil.copytree(repo, os.path.join(self.package_repos, name))

        tty.msg(f"Adding repositories to env: {self.env.name}....")
        env = get_env_as_dict(self.env)
        env["spack"]["repos"] = to_write
        self._write(env)

    def configure_package_settings(self, filter_externals=False):
        tty.msg(f"Add package settings to env: {self.env.name}....")
        with self.orig:
            package_settings = {}
            for scope in valid_env_scopes(self.orig):
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
        with self.orig:
            tty.msg(f"Creating mirror at {self.mirror}....")
            create_mirror_for_all_specs(
                mirror_specs=filter_externals(self.orig.all_specs()),
                path=self.mirror,
                skip_unstable_versions=False,
            )

        with self.env:
            tty.msg(f"Updating mirror at {self.mirror}....")
            create_mirror_for_all_specs(
                mirror_specs=filter_externals(self.env.all_specs()),
                path=self.mirror,
                skip_unstable_versions=False,
            )
            mirror_path = os.path.join(
                os.path.relpath(self.path, self.env.path), os.path.basename(self.mirror)
            )

            mirrorer = SpackCommand("mirror")
            tty.msg(f"Adding mirror to env: {self.env.name}....")
            with self.env.write_transaction():
                mirrorer("add", "internal", mirror_path)

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
            with working_dir(self.env.path):
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
            shutil.copytree(self.extra_data, self.path, dirs_exist_ok=True)

    def _write(self, data):
        with open(os.path.join(self.env.path, "spack.yaml"), "w") as outf:
            spack.util.spack_yaml.dump(data, outf, default_flow_style=False)

    def __enter__(self):
        self._cached_env = environment.active_environment()
        tty.msg(f"Concretizing env: {self.orig.name}....")
        self.orig.concretize()
        self.orig.write()
        environment.deactivate()
        self.wipe_n_make()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.filter_excludes()
        self.clean()
        if self._cached_env:
            environment.activate(self._cached_env)


def distribution(parser, args):
    env = spack.cmd.require_active_env(cmd_name="manager distribution")
    packager = DistributionPackager(
        env,
        args.distro_dir,
        includes=args.include,
        excludes=args.exclude,
        extra_data=args.extra_data,
    )
    with packager:
        packager.configure_specs()
        packager.configure_includes()
        packager.configure_extensions()
        packager.configure_package_repos()
        packager.configure_package_settings(filter_externals=args.filter_externals)
        packager.filter_excludes_and_concretize()
        packager.configure_source_mirror()
        packager.configure_bootstrap_mirror()
        packager.bundle_spack()
        packager.bundle_extra_data()
