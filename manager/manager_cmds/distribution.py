import argparse
import fnmatch
import glob
import os
import shutil

import spack.cmd
import spack.cmd.add
import spack.cmd.bootstrap
import spack.cmd.buildcache
import spack.cmd.config
import spack.cmd.mirror
import spack.config
import spack.environment
import spack.extensions
import spack.llnl.util.filesystem as fs
import spack.llnl.util.tty as tty
import spack.spec
import spack.util.path
import spack.util.spack_yaml
from spack.paths import spack_root

description = "bundle an environment as a self-contained source distribution"
section = "manager"
level = "long"


SPACK_USER_PATTERNS = ["var/*", "opt/*", ".git*", "etc/spack/*"]
SKIP_CONFIG_SECTION = ["mirrors", "repos", "include", "packages", "ci", "cdash", "bootstrap"]


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
        "--exclude-configs",
        type=parse_comma_separated,
        help=(
            "Sections in the environment's configuration file to exclude \
            (comma-separated string without spaces)"
        ),
    )
    subparser.add_argument(
        "--exclude-file",
        help="Sections in the enviroment's configuration file to exclude located a file",
    )
    subparser.add_argument(
        "--exclude-specs",
        type=parse_comma_separated,
        help="specs which Spack should not try to add to a mirror (specified on command line)",
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


def parse_comma_separated(value):
    return [item.strip() for item in value.split(",")]


def _read_config(filename):
    return spack.config.read_config_file(filename)


def get_env_as_dict(env):
    return _read_config(os.path.join(env.path, "spack.yaml"))


def is_match(string, patterns):
    return any(fnmatch.fnmatch(string, pattern) for pattern in patterns)


def read_yaml_file(filename):
    data = {}
    with open(filename, "r", encoding="utf-8") as f:
        data = spack.util.spack_yaml.load(f)
    return data


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


def valid_env_scopes(env):
    scopes = spack.config.CONFIG.matching_scopes(f"^env:{env.name}|^include:")
    return [s.name for s in scopes]


def bundle_spack(location):
    tty.msg(f"Packing up Spack installation to {location}....")
    copy_files_excluding_pattern(spack_root, location, SPACK_USER_PATTERNS)


def get_relative_paths(original_paths, env_path, dir_name):
    new_path = []
    for path in original_paths:
        path = os.path.join(os.path.relpath(dir_name, env_path), os.path.basename(path))
        new_path.append(path)
    return new_path


def call(module, method, args):
    sargs = " ".join(args)
    tty.msg(f"Executing: spack {method} {sargs}")
    parser = argparse.ArgumentParser()
    module.setup_parser(parser)
    args = parser.parse_args(args)
    callme = getattr(module, method)
    callme(parser, args)


class DistributionPackager:
    def __init__(
        self, env, root, includes=None, exclude_configs=None, exclude_file=None, extra_data=None
    ):
        self.environment_to_package = env
        self.includes = includes
        self.exclude_configs = []
        if exclude_file:
            self.exclude_configs.extend(read_yaml_file(exclude_file)["excludes"])
        if exclude_configs:
            self.exclude_configs.extend(exclude_configs)
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

    def __enter__(self):
        self._cached_env = spack.environment.active_environment()
        tty.msg(f"Concretizing env: {self.environment_to_package.name}....")
        self.environment_to_package.concretize()
        self.environment_to_package.write()
        spack.environment.deactivate()
        self.init_distro_dir()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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

    def init_config(self):
        flattened_config = self._get_flattened_config()
        with self.environment_to_package:
            flattened_config["config"]["extensions"] = get_relative_paths(
                spack.extensions.get_extension_paths(), self.env.path, self.extensions
            )
        self._create_config_file(flattened_config)

    def _get_flattened_config(self):
        flattened_config = {}
        with self.environment_to_package:
            for section in spack.config.SECTION_SCHEMAS:
                if section in SKIP_CONFIG_SECTION:
                    continue
                try:
                    flattened_config[section] = spack.config.CONFIG.get(section)
                except spack.config.ConfigSectionError as e:
                    tty.error(
                        f"The configuration section: {section} does not exist in \
                            {self.environment_to_package.name}. The error returned is: {e}"
                    )
        return flattened_config

    def _create_config_file(self, flattened_config):
        with self.env:
            for section in flattened_config:
                if flattened_config[section]:
                    try:
                        spack.config.CONFIG.set(
                            section, flattened_config[section], scope=self.env.scope_name
                        )
                    except spack.config.ConfigFormatError as e:
                        tty.error(
                            f"The configuration section: {section} has incorrect syntax \
                                in the environment. The error returned is: {e}"
                        )

    def filter_exclude_configs(self):
        if self.exclude_configs:
            with self.env:
                tty.msg(f"Excluding configurations: {self.exclude_configs}....")
                for exclude in self.exclude_configs:
                    with self.env.write_transaction():
                        call(spack.cmd.config, "config", ["remove", exclude])

    def configure_includes(self):
        if self.includes:
            tty.msg(f"Adding include dir to env: {self.env.name}....")
            includes_install = os.path.join(self.path, os.path.basename(self.includes))
            shutil.copytree(self.includes, includes_install)
            includes = os.path.relpath(includes_install, self.env.path)
            with self.env:
                with self.env.write_transaction():
                    call(spack.cmd.config, "config", ["add", f"include:[{includes}]"])

    def configure_specs(self):
        with self.environment_to_package:
            specs = self.environment_to_package.user_specs.specs_as_yaml_list

        tty.msg(f"Adding specs to env: {self.env.name}....")
        with self.env:
            with self.env.write_transaction():
                call(spack.cmd.add, "add", specs)

    def copy_extensions_files(self):
        with self.environment_to_package:
            tty.msg(f"Packing up extensions to {self.extensions}....")
            extensions = spack.extensions.get_extension_paths()
            os.makedirs(self.extensions)
            for extension in extensions:
                shutil.copytree(
                    extension,
                    os.path.join(self.extensions, os.path.basename(extension)),
                    ignore=shutil.ignore_patterns(".git*", "spack"),
                )

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

    def configure_source_mirror(self, filter_specs=None):
        # We do not want to omit any packages that are externals
        # just So They Build Faster internally, but are still needed externally.
        # However, this causes issues for packages that are not downloadable,
        # so we do a first-shot mirror creation with the original environment active.
        if filter_specs:
            filter_specs = [f"--exclude-specs={x}"for x in filter_specs]
        else:
            filter_specs = []

        with self.environment_to_package:
            tty.msg(f"Creating source mirror at {self.source_mirror}....")
            specs = [x.name for x in self.environment_to_package.all_specs()]
            args = [
                "create",
                "--directory",
                self.source_mirror,
                *filter_specs,
                *specs,
            ]
            call(spack.cmd.mirror, "mirror", args)

        with self.env:
            tty.msg(f"Updating mirror at {self.source_mirror}....")
            specs = [x.name for x in self.env.all_specs()]
            args = [
                "create",
                "--directory",
                self.source_mirror,
                *filter_specs,
                *specs,
            ]
            call(spack.cmd.mirror, "mirror", args)

            mirror_path = os.path.join(
                os.path.relpath(self.path, self.env.path), os.path.basename(self.source_mirror)
            )
            tty.msg(f"Adding mirror to env: {self.env.name}....")
            with self.env.write_transaction():
                call(spack.cmd.mirror, "mirror", ["add", "internal-source", mirror_path])

    def configure_binary_mirror(self):
        with self.environment_to_package:
            tty.msg(f"Creating binary mirror at {self.binary_mirror}....")
            call(spack.cmd.buildcache, "buildcache", ["push", "--unsigned", self.binary_mirror])
            call(spack.cmd.buildcache, "buildcache", ["keys", "--install", "--trust"])

        mirror_path = os.path.join(
            os.path.relpath(self.path, self.env.path), os.path.basename(self.binary_mirror)
        )
        mirror_name = "internal-binary"

        with self.env:
            tty.msg(f"Adding mirror to env: {self.env.name}....")
            with self.env.write_transaction():
                call(
                    spack.cmd.mirror,
                    "mirror",
                    ["add", "--type", "binary", "--unsigned", mirror_name, mirror_path],
                )

    def configure_bootstrap_mirror(self):
        tty.msg(f"Creating bootstrap mirror at {self.bootstrap_mirror}....")
        parser = argparse.ArgumentParser()
        spack.cmd.bootstrap.setup_parser(parser)

        with self.environment_to_package:
            call(
                spack.cmd.bootstrap,
                "bootstrap",
                ["mirror", "--binary-packages", self.bootstrap_mirror],
            )

            bootstrap_source = os.path.join(
                os.path.relpath(self.bootstrap_mirror, self.env.path), "metadata", "sources"
            )
            bootstrap_binary = os.path.join(
                os.path.relpath(self.bootstrap_mirror, self.env.path), "metadata", "binaries"
            )

        with self.env:
            with fs.working_dir(self.env.path):
                with self.env.write_transaction():
                    call(
                        spack.cmd.bootstrap,
                        "bootstrap",
                        [
                            "add",
                            "--trust",
                            "--scope",
                            f"env:{self.env.name}",
                            "internal-sources",
                            bootstrap_source,
                        ],
                    )
                with self.env.write_transaction():
                    call(
                        spack.cmd.bootstrap,
                        "bootstrap",
                        [
                            "add",
                            "--trust",
                            "--scope",
                            f"env:{self.env.name}",
                            "internal-binary",
                            bootstrap_binary,
                        ],
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
        exclude_configs=args.exclude_configs,
        exclude_file=args.exclude_file,
        extra_data=args.extra_data,
    )

    with packager:
        packager.init_config()
        packager.filter_exclude_configs()
        packager.configure_includes()
        packager.configure_specs()
        packager.copy_extensions_files()
        packager.configure_package_repos()
        packager.configure_package_settings(filter_externals=args.filter_externals)
        packager.configure_bootstrap_mirror()
        packager.concretize()
        if not args.binary_only:
            packager.configure_source_mirror(filter_specs=args.exclude_specs)
        if not args.source_only:
            packager.configure_binary_mirror()
        packager.bundle_spack()
        packager.bundle_extra_data()
