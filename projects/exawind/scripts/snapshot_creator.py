#!/usr/bin/env spack-python
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

"""
This script will create the snapshots we need for the exawind project
and any associated modules
"""

import argparse
import multiprocessing
import os
import sys

from environment_utils import SpackManagerEnvironmentManifest
from manager_cmds.find_machine import find_machine
from manager_utils import path_extension, pruned_spec_string

import spack.cmd.install
import spack.environment as ev
import spack.main
import spack.util.executable
import spack.util.spack_yaml as syaml
from spack.spec import Spec
from spack.version import GitVersion, Version

git = spack.util.executable.which("git")

manager = spack.main.SpackCommand("manager")
add = spack.main.SpackCommand("add")
concretize = spack.main.SpackCommand("concretize")
module = spack.main.SpackCommand("module")

base_spec = "exawind+hypre+openfast"

blacklist = ["cuda", "yaml-cpp", "rocm", "llvm-admgpu", "hip", "py-"]


def spack_install_cmd(args):
    """
    manually call spack.install so we get output
    """
    parser = argparse.ArgumentParser("dummy parser")
    # this is missing from the parser but not really used so we create a dummy
    parser.add_argument("--not_used", dest="verbose", required=False)
    spack.cmd.install.setup_parser(parser)
    parsed_args = parser.parse_args(args)
    print(parsed_args)
    spack.cmd.install.install(parser, parsed_args)


def command(command, *args):
    """
    Execute a spack.main.SpackCommand uniformly
    and add some print statements
    """
    print("spack", command.command_name, *args)
    print(command(*args, fail_on_error=False))


class SnapshotSpec:
    """
    Data structure for storing a tag that is not a hash
    to represent the spec added to the spack.yaml
    """

    def __init__(self, id="default", spec=base_spec, exclusions=[]):
        self.id = id
        self.spec = spec
        self.exclusions = exclusions


# a list of specs to build in the snapshot, 1 view will be created for each
machine_specs = {
    "darwin": [SnapshotSpec(exclusions=["%intel"])],
    "cee": [SnapshotSpec()],
    "e4s": [
        SnapshotSpec(),
        SnapshotSpec(id="amr-standalone", spec="amr-wind+hypre+openfast+masa"),
    ],
    "rhodes": [
        SnapshotSpec("gcc", base_spec + "%gcc", ["%clang", "%intel"]),
        SnapshotSpec("clang", base_spec + "%clang", ["%gcc", "%intel"]),
        SnapshotSpec("intel", base_spec + "%intel", ["%gcc", "%clang"]),
    ],
    "eagle": [
        SnapshotSpec("gcc", base_spec + "%gcc", ["%clang", "%intel"]),
        SnapshotSpec("clang", base_spec + "%clang", ["%gcc", "%intel"]),
        SnapshotSpec("intel", base_spec + "%intel", ["%gcc", "%clang"]),
        SnapshotSpec(
            "gcc-cuda",
            base_spec + "+cuda+amr_wind_gpu+nalu_wind_gpu " "cuda_arch=70 %gcc",
            ["%clang", "%intel"],
        ),
    ],
    "summit": [
        SnapshotSpec("gcc", "exawind+hypre" "~cuda~amr_wind_gpu~nalu_wind_gpu %gcc"),
        SnapshotSpec(
            "cuda", "exawind+hypre" "+cuda+amr_wind_gpu+nalu_wind_gpu " "cuda_arch=70 %gcc"
        ),
    ],
    "snl-hpc": [SnapshotSpec()],
}


def parse(stream):
    parser = argparse.ArgumentParser("create a timestamped snapshot for registered machines")
    parser.add_argument(
        "-m",
        "--modules",
        action="store_true",
        help="create modules to associate with each view in the environment",
    )
    phases = ["create_env", "mod_specs", "concretize", "install"]
    parser.add_argument("--stop_after", "-sa", choices=phases, help="stop script after this phase")
    parser.add_argument(
        "--use_develop",
        "-ud",
        action="store_true",
        help="use develop specs for roots and their immediate " "dependencies",
    )
    parser.add_argument(
        "--name",
        "-n",
        required=False,
        help="name the environment something other than the " "date",
    )
    parser.add_argument(
        "--use_machine_name",
        "-mn",
        action="store_true",
        help="use machine name in the snapshot path " "instead of computed architecture",
    )
    parser.add_argument(
        "--spack_install_args",
        "-sai",
        required=False,
        default=[],
        help="arguments to forward to spack install",
    )
    parser.add_argument(
        "--num_threads",
        "-nt",
        type=int,
        default=1,
        help="number of threads to use for calling spack " "install (parallel DAG install)",
    )
    parser.add_argument(
        "--link_type",
        "-lt",
        required=False,
        choices=["symlink", "soft", "hardlink", "hard," "copy", "relocate"],
        help="set the type of" " linking used in view creation",
    )
    parser.set_defaults(
        modules=False, use_develop=False, stop_after="install", link_type="symlink"
    )

    return parser.parse_args(stream)


def view_excludes(snap_spec):
    if "+cuda" in snap_spec.spec:
        snap_spec.exclusions.extend(["+rocm", "~cuda"])
    elif "+rocm" in snap_spec.spec:
        snap_spec.exclusions.extend(["~rocm", "+cuda"])
    else:
        snap_spec.exclusions.extend(["+rocm", "+cuda"])
    return snap_spec.exclusions.copy()


def add_view(env, extension, link_type):
    view_path = os.path.join(os.environ["SPACK_MANAGER"], "views", extension, "snapshot")
    view_dict = {
        "snapshot": {
            "root": view_path,
            "projections": {
                "all": "{compiler.name}-{compiler.version}/{name}/" "{version}-{hash:4}",
                "^cuda": "{compiler.name}-{compiler.version}-"
                "{^cuda.name}-{^cuda.version}/{name}/{version}"
                "-{hash:4}",
                "^rocm": "{compiler.name}-{compiler.version}-"
                "{^rocm.name}-{^rocm.version}/{name}/{version}"
                "-{hash:4}",
            },
            "link_type": link_type,
        }
    }
    with open(env.manifest_path, "r") as f:
        yaml = syaml.load(f)
    # view yaml entry can also be a bool so first try to add to a dictionary,
    # and if that fails overwrite entry as a dictionary
    try:
        yaml["spack"]["view"].update(view_dict)
    except AttributeError:
        yaml["spack"]["view"] = view_dict

    with open(env.manifest_path, "w") as f:
        syaml.dump(yaml, stream=f, default_flow_style=False)


def add_spec(env, extension, data, create_modules):
    ev.activate(env)
    add(data.spec)
    ev.deactivate()
    excludes = view_excludes(data)

    with open(env.manifest_path, "r") as f:
        yaml = syaml.load(f)

    if create_modules:
        module_excludes = excludes.copy()
        module_path = os.path.join(os.environ["SPACK_MANAGER"], "modules")
        module_dict = {
            data.id: {
                "enable": ["tcl"],
                "use_view": data.id,
                "prefix_inspections": {"bin": ["PATH"]},
                "roots": {"tcl": module_path},
                "arch_folder": False,
                "tcl": {
                    "projections": {"all": "%s/{name}-%s" % (extension, data.id)},
                    "hash_length": 0,
                    "blacklist_implicits": True,
                    "blacklist": module_excludes,
                },
            }
        }
        try:
            yaml["spack"]["modules"].update(module_dict)
        except KeyError:
            yaml["spack"]["modules"] = module_dict

    with open(env.manifest_path, "w") as f:
        syaml.dump(yaml, stream=f, default_flow_style=False)


def get_top_level_specs(env, blacklist=blacklist):
    ev.activate(env)
    print("\nInitial concretize")
    command(concretize, "-f")
    top_specs = []
    for root in env.roots():
        if root.name in blacklist:
            continue
        top_specs.append(root)
        for dep in root.dependencies():
            if dep.name not in blacklist:
                top_specs.append(dep)
    # remove any duplicates
    top_specs = list(dict.fromkeys(top_specs))
    print("\nTop Level Specs:", [s.name for s in top_specs])
    ev.deactivate()
    return top_specs


def find_latest_git_hash(spec):
    if isinstance(spec.version, GitVersion):
        # if it is already a GitVersion then we've probably already ran this
        # once we are going to recreate the paried version that the git hash
        # has been assigned to and use that
        version = Version(spec.version.ref_version_str)
        version_dict = spec.package_class.versions[version]
    else:
        version_dict = spec.package_class.versions[spec.version]
    keys = version_dict.keys()

    if "branch" in keys:
        # git branch
        ref = "refs/heads/%s" % version_dict["branch"]
    elif "tag" in keys:
        # already matched
        return None
    elif "sha256" in keys:
        # already matched
        return None
    elif "commit" in keys:
        # we could reuse the commit, but since it is effectively pinned just
        # return none
        return None
    else:
        raise Exception("no known git type for " + spec.format("//{hash} ({name}{@version})"))

    # get the matching entry and shas for github
    query = git("ls-remote", spec.package.git, ref, output=str, error=str).strip().split("\n")
    assert len(query) == 1

    sha, _ = query[0].split("\t")

    return sha


def replace_versions_with_hashes(spec_string, hash_dict):
    specs = str(spec_string).strip().split(" ^")
    new_specs = []
    for spec in specs:
        base, rest = spec.split("%")
        name, version = base.split("@")

        # use paired version if it is already a GitVersion
        newSpec = Spec(spec)
        if isinstance(newSpec.version, GitVersion):
            version = newSpec.version.ref_version_str

        hash = hash_dict.get(name)
        if hash:
            version = "git.{hash}={version}".format(hash=hash, version=version)
            # prune the spec string to get rid of patches which could cause
            # conflicts later
            new_specs.append(pruned_spec_string("{n}@{v}%{r}".format(n=name, v=version, r=rest)))
    final = " ^".join(new_specs)
    assert "\n" not in final
    assert "\t" not in final
    return final


def use_latest_git_hashes(env, blacklist=blacklist):
    with open(env.manifest_path, "r") as f:
        yaml = syaml.load(f)

    roots = list(env.roots())

    for i in range(len(roots)):
        if roots[i].name not in blacklist:
            hash_dict = {}
            hash_dict[roots[i].name] = find_latest_git_hash(roots[i])

            for dep in roots[i].dependencies():
                if dep.name not in blacklist:
                    hash_dict[dep.name] = find_latest_git_hash(dep)

            yaml["spack"]["specs"][i] = replace_versions_with_hashes(
                roots[i].build_spec, hash_dict
            )

    with open(env.manifest_path, "w") as fout:
        syaml.dump_config(yaml, stream=fout, default_flow_style=False)
    env._re_read()


def use_develop_specs(env, specs):
    # we have to concretize to solve the dependency tree to extract
    # the top level dependencies and make them develop specs.
    # anything that is not a develop spec is not gauranteed to get installed
    # since spack can reuse them for matching hashes

    print("\nSetting up develop specs")
    dev_specs = list(dict.fromkeys([s.format("{name}{@version}") for s in specs]))

    ev.activate(env)
    for spec_string in dev_specs:
        # special treatment for trilinos since its clone fails
        # with standard spack develop
        if "trilinos" in spec_string:
            branch = spec_string.split("@")[-1]
            command(
                manager,
                "develop",
                "--shallow",
                "-rb",
                "https://github.com/trilinos/trilinos",
                branch,
                spec_string,
            )
        elif "openfast" in spec_string:
            # skip openfast. we never want to dev build it
            # because it takes so long to compile
            continue
        elif "cmake" in spec_string:
            continue
        else:
            command(manager, "develop", "--shallow", spec_string)
    ev.deactivate()


def create_snapshots(args):
    machine = find_machine(verbose=False)
    extension = path_extension(args.name, args.use_machine_name)
    env_path = os.path.join(os.environ["SPACK_MANAGER"], "environments", extension)

    print("\nCreating snapshot environment")

    command(manager, "create-env", "-d", env_path)

    e = ev.Environment(env_path)

    manifest = SpackManagerEnvironmentManifest(env_path)
    manifest.set_config_value("concretizer", "unify", "when_possible")
    manifest.flush()

    spec_data = machine_specs[machine]
    add_view(e, extension, args.link_type)
    for s in spec_data:
        add_spec(e, extension, s, args.modules)

    top_specs = get_top_level_specs(e)

    if args.stop_after == "create_env":
        return

    if args.use_develop:
        use_develop_specs(e, top_specs)
    else:
        use_latest_git_hashes(e)

    if args.stop_after == "mod_specs":
        return

    ev.activate(e)
    print("\nConcretize")
    command(concretize, "-f")
    if args.stop_after == "concretize":
        return
    print("\nInstall")
    with multiprocessing.Pool(args.num_threads):
        spack_install_cmd(args.spack_install_args)

    if args.modules:
        print("\nGenerate module files")
        command(module, "tcl", "refresh", "-y")
    return env_path


if __name__ == "__main__":
    args = parse(sys.argv[1:])
    create_snapshots(args)
