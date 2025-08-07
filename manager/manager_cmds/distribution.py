import os
import fnmatch
import shutil

import spack
from spack import environment
from spack.cmd.mirror import create_mirror_for_all_specs, filter_externals
from spack.paths import spack_root
from spack import config
from spack.main import SpackCommand

from llnl.util.filesystem import working_dir
from spack.config import SECTION_SCHEMAS as sc_section_schemas


description = "bundle an environment as a self-contained source distribution"
section = "manager"
level = "long"


def add_command(parser, command_dict):
    subparser =parser.add_parser(
        "distribution",
        help=description,
    )
    subparser.add_argument(
        "--include",
        help="Directory containg yaml to be included in the packaged environment",
    )

    subparser.add_argument(
        "--exclude",
        help="Directory containg yaml to be explicitly removed from packaged environment",
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
    #FIXME: Would it be better to use some portion of includes_creator here?
    sections = list(spack.config.SECTION_SCHEMAS.keys())
    aconfig = spack.config.Configuration()
    scope = spack.config.DDirectoryConfigScopeirectoryScope(name, os.path.abspath(path))
    aconfig.push_scope(scope)
    scope = aconfig.scopes[name]

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


def update_package_data(package, data, package_data):
    if "externals" not in data:
        try:
            package_data[package].update(data)
        except KeyError:
            package_data[package] = data


def wipe_n_make(directory):
    print("Precleaning....")
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)


def valid_env_scopes(env):
    scopes = spack.config.CONFIG.matching_scopes(f"^env:{env.name}|^{spack.config.INCLUDE_SCOPE_PREFIX}")
    return [s.name for s in scopes]



def create_package_env(directory):
    return environment.create_in_dir(directory, keep_relative=True)


def add_specs_to_env(new_env, old_env):
    with old_env:
        specs = old_env.user_specs.specs_as_yaml_list
    
    adder = SpackCommand("add")
    print(f"Adding specs to env: {new_env.name}....")
    with new_env:
        for spec in specs:
            with new_env.write_transaction():
                adder(spec)


def add_repositories_to_env(new_env, old_env, repo_location):
    repos = set()
    with old_env:
        for scope in valid_env_scopes(old_env):
            for repo in spack.config.get("repos", scope=scope):
                repos.add(spack.util.path.canonicalize_path(repo))

    print(f"Packing up package repositories to {repo_location}....")
    os.makedirs(repo_location)
    for repo in repos:
        shutil.copytree(repo, os.path.join(repo_location, os.path.basename(repo)))

    print(f"Adding up repositories to env: {new_env.name}....")
    sconfig = SpackCommand("config")
    with new_env:
        for repo in repos:
            repo = os.path.join(
                os.path.relpath(repo_location, new_env.path), os.path.basename(repo)
            )
            with new_env.write_transaction():
                sconfig("add", f"repos:[{repo}]")


def add_extensions_to_env(new_env, old_env, extension_location):
    with old_env:
        extensions = [x for x in spack.extensions.get_extension_paths() if "spack-manager" not in x]
    print(f"Packing up extensions to {extension_location}....")
    os.makedirs(extension_location)
    for extension in extensions:
        shutil.copytree(
            extension, os.path.join(extension_location, os.path.basename(extension))
        )

    print(f"Adding up extensions to env: {new_env.name}....")
    sconfig = SpackCommand("config")
    with new_env:
        with new_env:
            for extension in extensions:
                extension = os.path.join(
                    os.path.relpath(extension_location, new_env.path),
                    os.path.basename(extension),
                )
                with new_env.write_transaction():
                    sconfig("add", f"config:extensions:[{extension}]")




def _write(data, env):
    with open(os.path.join(env.path, "spack.yaml"), "w") as outf:
        spack.util.spack_yaml.dump(
            data, outf, default_flow_style=False
        )


def add_package_settings_to_env(new_env, old_env):
    print(f"Add package settings to env: {new_env.name}....")
    with old_env:
        package_settings = {}
        for scope in valid_env_scopes(old_env):
            for package, data in spack.config.get("packages", scope=scope).items():
                update_package_data(package,data, package_settings)
    #FIXME: It seems cumbersome to spack config add every aspect of the pacakge settings. Is there a better way?
    env_data = get_env_as_dict(new_env)
    env_data["spack"]["packages"] = package_settings
    _write(env_data, new_env)


def finalize_env(env, excludes):
    print(f"Writing manifest file for env: {env.name}....")
    env_data = get_env_as_dict(env)
    if excludes:
        print(f"Processign settings to exclude from env: {env.name}....")
        cfg = get_local_config("exclude", excludes)
        remove_subset_from_dict(env_data, cfg)
    _write(env_data, env)
    
    print(f"Concretizing env: {env.name}....")
    env.concretize(force=True)
    env.write()


def add_package_mirror(new_env, old_env, mirror_location, install_root):
    # We do not want to omit any packages that are externals 
    # just So They Build Faster internally, but are still needed externally.
    # However, this causes issues for packages that are not downloadable, 
    # so we do a first-shot mirror creation with the original environment active.
    with old_env:
        print(f"Creating mirror at {mirror_location}....")
        create_mirror_for_all_specs(
            mirror_specs=filter_externals(old_env.all_specs()),
            path=mirror_location,
            skip_unstable_versions=False,
        )

    mirrorer = SpackCommand("mirror")
    with new_env:
        print(f"Updating mirror at {mirror_location}....")
        create_mirror_for_all_specs(
            mirror_specs=filter_externals(new_env.all_specs()),
            path=mirror_location,
            skip_unstable_versions=False,
        )
        mirror_path = os.path.join(
                os.path.relpath(install_root, new_env.path), 
                os.path.basename(mirror_location),
            )
        print(f"Adding mirror to env: {new_env.name}....")
        with new_env.write_transaction():
            mirrorer("add", "internal", mirror_path)


def add_bootstrap_mirror(new_env, mirror_location):
        print(f"Creating bootstrap mirror at {mirror_location}....")
        strapper = SpackCommand("bootstrap")
        strapper("mirror", "--binary-packages", mirror_location)
        bootstrap_source = os.path.join(
            os.path.relpath(mirror_location, new_env.path),
            "metadata",
            "sources",
        )
        bootstrap_binary = os.path.join(
            os.path.relpath(mirror_location, new_env.path),
            "metadata",
            "binaries",
        )
        with new_env:
            with working_dir(new_env.path):
                with new_env.write_transaction():
                    strapper("add", "--trust", "--scope", f"env:{new_env.name}", "internal-sources", bootstrap_source)
                with new_env.write_transaction():
                    strapper("add", "--trust", "--scope", f"env:{new_env.name}", "internal-binaries", bootstrap_binary)


def package_spack(new_location):
    print(f"Packing up Spack installation to {new_location}....")
    ignore_these = ["var/spack/environments/*", "opt/*", ".git*", "etc/spack/include.yaml"]
    copy_files_excluding_pattern(
        spack_root,
        new_location,
        ignore_these,
    )


def clean(env):
    for item in os.listdir(env.path):
        fullname = os.path.join(env.path, item)
        if "spack.yaml" in item:
            continue
        elif os.path.isdir(fullname):
            shutil.rmtree(fullname)
        else:
            os.remove(fullname)


class DistributionPacakger:
    def __init__(self, env, root, includes, excludes):
        self.orig = env
        self.includes = includes
        self.excludes = excludes

        self.path = root
        self.package_repos = os.path.join(self.path, "package-repos")
        self.extensions = os.path.join(self.path, "extensions")
        self.mirror = os.path.join(self.path, "mirror")
        self.bootstrap_mirror = os.path.join(self.path, "bootstrap-mirror")

        self.wipe_n_make()
        self.env = environment.create_in_dir(os.path.join(self.path, "environment"), keep_relative=True)

    
    def wipe_n_make(self):
        print("Precleaning....")
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)
        os.makedirs(self.path)
    
    def finalize(self):
        print(f"Writing manifest file for env: {self.env.name}....")
        env_data = get_env_as_dict(self.env)
        if self.excludes:
            print(f"Processign settings to exclude from env: {self.env.name}....")
            cfg = get_local_config("exclude", self.excludes)
            remove_subset_from_dict(env_data, cfg)
        self._write(env_data)
        
        print(f"Concretizing env: {self.env.name}....")
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

    def configure_specs(self):
        with self.orig:
            specs = self.orig.user_specs.specs_as_yaml_list
    
        adder = SpackCommand("add")
        print(f"Adding specs to env: {self.env.name}....")
        with self.env:
            for spec in specs:
                with self.env.write_transaction():
                    adder(spec)

    def configure_extensions(self):
        with self.orig:
            extensions = [x for x in spack.extensions.get_extension_paths() if "spack-manager" not in x]
            print(f"Packing up extensions to {self.extensions}....")
            os.makedirs(self.extensions)
            for extension in extensions:
                shutil.copytree(
                    extension, os.path.join(self.extensions, os.path.basename(extension))
                )

        print(f"Adding up extensions to env: {self.env.name}....")
        sconfig = SpackCommand("config")
        with self.env:
            for extension in extensions:
                extension = os.path.join(
                    os.path.relpath(self.extensions, self.env.path),
                    os.path.basename(self.extensions),
                )
                with self.env.write_transaction():
                    sconfig("add", f"config:extensions:[{extension}]")

    def configure_package_repos(self):
        repos = set()
        with self.orig:
            for scope in valid_env_scopes(self.orig):
                for repo in spack.config.get("repos", scope=scope):
                    repos.add(spack.util.path.canonicalize_path(repo))

        print(f"Packing up package repositories to {self.package_repos}....")
        os.makedirs(self.package_repos)
        for repo in repos:
            shutil.copytree(repo, os.path.join(self.package_repos, os.path.basename(repo)))

        print(f"Adding up repositories to env: {self.env.name}....")
        sconfig = SpackCommand("config")
        with self.env:
            for repo in repos:
                repo = os.path.join(
                    os.path.relpath(self.package_repos, self.env.path), os.path.basename(repo)
                )
                with self.env.write_transaction():
                    sconfig("add", f"repos:[{repo}]")

    def configure_package_settings(self):
        print(f"Add package settings to env: {self.env.name}....")
        with self.orig:
            package_settings = {}
            for scope in valid_env_scopes(self.orig):
                for package, data in spack.config.get("packages", scope=scope).items():
                    if "externals" not in data:
                        try:
                            package_settings[package].update(data)
                        except KeyError:
                            package_settings[package] = data
        #FIXME: It seems cumbersome to spack config add every aspect of the pacakge settings. Is there a better way?
        env_data = get_env_as_dict(self.env)
        env_data["spack"]["packages"] = package_settings
        self._write(env_data)

    def configure_package_mirror(self):
        # We do not want to omit any packages that are externals 
        # just So They Build Faster internally, but are still needed externally.
        # However, this causes issues for packages that are not downloadable, 
        # so we do a first-shot mirror creation with the original environment active.
        with self.orig:
            print(f"Creating mirror at {self.mirror}....")
            create_mirror_for_all_specs(
                mirror_specs=filter_externals(self.orig.all_specs()),
                path=self.mirror,
                skip_unstable_versions=False,
            )

        mirrorer = SpackCommand("mirror")
        with self.env:
            print(f"Updating mirror at {self.mirror}....")
            create_mirror_for_all_specs(
                mirror_specs=filter_externals(self.env.all_specs()),
                path=self.mirror,
                skip_unstable_versions=False,
            )
            mirror_path = os.path.join(
                    os.path.relpath(self.path, self.env.path), 
                    os.path.basename(self.mirror),
                )
            print(f"Adding mirror to env: {self.env.name}....")
            with self.env.write_transaction():
                mirrorer("add", "internal", mirror_path)

    def configure_bootstrap_mirror(self):
        print(f"Creating bootstrap mirror at {self.bootstrap_mirror}....")
        strapper = SpackCommand("bootstrap")
        strapper("mirror", "--binary-packages", self.bootstrap_mirror)
        bootstrap_source = os.path.join(
            os.path.relpath(self.bootstrap_mirror, self.env.path),
            "metadata",
            "sources",
        )
        bootstrap_binary = os.path.join(
            os.path.relpath(self.bootstrap_mirror, self.env.path),
            "metadata",
            "binaries",
        )
        with self.env:
            with working_dir(self.env.path):
                with self.env.write_transaction():
                    strapper("add", "--trust", "--scope", f"env:{self.env.name}", "internal-sources", bootstrap_source)
                with self.env.write_transaction():
                    strapper("add", "--trust", "--scope", f"env:{self.env.name}", "internal-binaries", bootstrap_binary)

    def bundle_spack(self):
        install_here = os.path.join(self.path, "spack")
        print(f"Packing up Spack installation to {install_here}....")
        ignore_these = ["var/spack/environments/*", "opt/*", ".git*", "etc/spack/include.yaml"]
        copy_files_excluding_pattern(
            spack_root,
            install_here,
            ignore_these,
        )

    def _write(self, data):
        with open(os.path.join(self.env.path, "spack.yaml"), "w") as outf:
            spack.util.spack_yaml.dump(
                data, outf, default_flow_style=False
            )

    def __enter__(self):
        print(f"Concretizing env: {self.orig.name}....")
        self.orig.concretize()
        self.orig.write()
        environment.deactivate()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finalize()
        self.clean()


def distribution(parser, args):
    env = spack.cmd.require_active_env(cmd_name="manager distribution")
    distro = os.path.join(os.getcwd(), "distro")
    # wipe_n_make(distro)

    with DistributionPacakger(env, distro, args.include, args.exclude) as pkg:
        pkg.configure_specs()
        pkg.configure_extensions()
        pkg.configure_package_repos()
        pkg.configure_package_settings()
        pkg.finalize()
        pkg.configure_package_mirror()
        pkg.configure_bootstrap_mirror()
        # pkg.bundle_spack()

    # mirror = os.path.join(distro, "mirror")
    # bootstrap_mirror = os.path.join(distro, "bootstrap-mirror")
    # spack_install = os.path.join(distro, "spack")
    # repos_install = os.path.join(distro, "package-repos")
    # extensions_install = os.path.join(distro, "extensions")

    # install_env = os.path.join(distro, "environment")
    # pkg_env = create_package_env(install_env)

    # print("Concretizing....")
    # env.concretize()
    # env.write()
    # env.deactivate()

    # add_specs_to_env(pkg_env, env)
    # add_extensions_to_env(pkg_env, env, extensions_install)
    # add_repositories_to_env(pkg_env, env, repos_install)
    # add_package_settings_to_env(pkg_env, env)
    # finalize_env(pkg_env, args.exclude)
    # add_package_mirror(pkg_env, env, mirror, distro)
    # add_bootstrap_mirror(pkg_env, bootstrap_mirror)
    # finalize_env(pkg_env, args.exclude)
    # clean(pkg_env)
    # package_spack(spack_install)
    raise SystemExit()
    