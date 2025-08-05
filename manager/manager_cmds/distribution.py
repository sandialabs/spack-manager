import os
import shutil
import sys

from spack import environment
from spack.cmd.mirror import create_mirror_for_all_specs, filter_externals
from spack.paths import spack_root
from spack import config
from spack.main import SpackCommand

description = "bundle an environment as a self-contained source distribution"
section = "manager"
level = "long"


def add_command(parser, command_dict):
    subparser =parser.add_parser(
        "distribution",
        help=description,
    )
    subparser.add_argument(
        "--require-externals",
        nargs="+",
        default=[],
        help="require these packages to be external (do not include them in mirror, do not version restrict them)",
    )

    subparser.add_argument(
        "--allow-externals",
        nargs="+",
        default=[],
        help="allow these packages to be external (include them in mirror, but do not version restrict them)",
    )
    command_dict["distribution"] = distribution

def remove_entries_with_substrings(d, substrings):
    """
    Recursively remove entries from a dictionary that contain any of the specified substrings.

    :param d: The dictionary to process.
    :param substrings: A set of substrings to check against.
    """
    # Create a list of keys to remove
    keys_to_remove = []

    for key, value in d.items():
        # Check if the key contains any of the substrings
        if any(sub in key for sub in substrings):
            keys_to_remove.append(key)
        # If the value is a dictionary, recurse into it
        elif isinstance(value, dict):
            remove_entries_with_substrings(value, substrings)
            # If the dictionary becomes empty after recursion, mark it for removal
            if not value:
                keys_to_remove.append(key)
        elif isinstance(value, list):
            for v in value:
                if any(sub in v for sub in substrings):
                    keys_to_remove.append(key)

    # Remove the marked keys from the dictionary
    for key in keys_to_remove:
        del d[key]


def wipe_n_make(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)


def distribution(parser, args):
    env = spack.cmd.require_active_env(cmd_name="distribution")

    distro = os.path.join(os.getcwd(), "distro")
    print("Precleaning....")
    wipe_n_make(distro)
    mirror = os.path.join(distro, "mirror")
    bootstrap_mirror = os.path.join(distro, "bootstrap-mirror")
    spack_install = os.path.join(distro, "spack")
    repos_install = os.path.join(distro, "package-repos")
    install_env = os.path.join(distro, "environment")
    extensions_install = os.path.join(distro, "extensions")

    env.concretize()
    env.write()
    m = config.CONFIG

    repos = set()
    for x in m.scopes.keys():
        if x.startswith("env") or x.startswith("include"):
            for repo in m.get("repos", scope=x):
                if os.path.isabs(repo):
                    repos.add(repo)
                else:
                    repos.add(
                        os.path.normpath(
                            os.path.join(
                                os.path.dirname(
                                    m.get_config_filename(scope=x, section="repos")
                                ),
                                repo,
                            )
                        )
                    )
    print(f"Packing up package repositories to {repos_install}....")
    os.makedirs(repos_install)
    for repo in repos:
        shutil.copytree(repo, os.path.join(repos_install, os.path.basename(repo)))

    extensions = set()
    for x in m.scopes.keys():
        if x.startswith("env") or x.startswith("include"):
            for extension in m.get("config:extensions", scope=x, default=[]):
                if os.path.isabs(extension):
                    extensions.add(extension)
                else:
                    extensions.add(
                        os.path.normpath(
                            os.path.join(
                                os.path.dirname(
                                    m.get_config_filename(scope=x, section="config")
                                ),
                                extension,
                            )
                        )
                    )
    print(f"Packing up extensions to {extensions_install}....")
    os.makedirs(extensions_install)
    for extension in extensions:
        shutil.copytree(
            extension, os.path.join(extensions_install, os.path.basename(extension))
        )

    package_settings = {}
    for x in m.scopes.keys():
        if x.startswith("env") or x.startswith("include"):
            packages = m.get("packages", scope=x)
            for package, data in packages.items():
                if "externals" not in data:
                    try:
                        package_settings[package].update(data)
                    except KeyError:
                        package_settings[package] = data
    # Trim out information about the MPI provider, since we can't know what the user will point at to build
    # TODO: Decide how to handle the same issue for BLAS/LAPACK providers
    remove_entries_with_substrings(package_settings, {"%", "mpi"})
    print(f"Packing up Spack environment settings to {install_env}....")
    os.makedirs(install_env)
    big_config = {
        "config": {
            "extensions": [
                os.path.join(
                    os.path.relpath(extensions_install, install_env),
                    os.path.basename(extension),
                )
                for extension in extensions
            ]
        },
        "repos": [
            os.path.join(
                os.path.relpath(repos_install, install_env), os.path.basename(repo)
            )
            for repo in repos
        ],
        "mirrors": {
            "internal": os.path.join(
                os.path.relpath(distro, install_env), os.path.basename(mirror)
            )
        },
        "bootstrap": {
            "sources": [
                {
                    "name": "internal-binaries",
                    "metadata": os.path.join(
                        os.path.relpath(bootstrap_mirror, install_env),
                        "metadata",
                        "binaries",
                    ),
                },
                {
                    "name": "internal-sources",
                    "metadata": os.path.join(
                        os.path.relpath(bootstrap_mirror, install_env),
                        "metadata",
                        "sources",
                    ),
                },
            ],
            "trusted": {"internal-binaries": True, "internal-sources": True},
        },
        "specs": env.user_specs.specs_as_yaml_list,
    }
    big_config["packages"] = package_settings
    with open(os.path.join(install_env, "spack.yaml"), "w") as outf:
        spack.util.spack_yaml.dump(
            {"spack": big_config}, outf, default_flow_style=False
        )

    print(f"Packing up Spack installation to {spack_install}....")
    shutil.copytree(
        spack_root,
        spack_install,
        ignore=lambda _, files: [".git"] if ".git" in files else [],
    )
    # TODO: Do not copy the site install config files
    badfile = os.path.join(spack_install, "etc", "spack", "include.yaml")
    if os.path.isfile(badfile):
        os.remove(badfile)

    # We deactivate the environment and use the special one we created so that the concretization will be the same.
    #  Specifically, we do not want to omit any packages that are externals Just So They Build Faster internally, but are still needed externally.
    #  However, this causes issues for packages that are not downloadable, so we do a first-shot mirror creation with the original environment active.
    print(f"Creating mirror at {mirror}....")
    create_mirror_for_all_specs(
        mirror_specs=filter_externals(env.all_specs()),
        path=mirror,
        skip_unstable_versions=False,
    )
    print("Activating package environment to remove externals....")
    environment.deactivate()
    env = environment.Environment(manifest_dir=install_env)
    environment.activate(env)
    env.concretize()
    print(f"Creating bootstrap mirror at {bootstrap_mirror}....")
    strapper = SpackCommand("bootstrap")
    strapper("mirror", "--binary-packages", bootstrap_mirror)
    print(f"Creating mirror (ignoring declared externals) at {mirror}....")
    create_mirror_for_all_specs(
        mirror_specs=filter_externals(env.all_specs()),
        path=mirror,
        skip_unstable_versions=False,
    )
