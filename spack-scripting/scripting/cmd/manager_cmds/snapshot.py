# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
import argparse

import snapshot_utils as sutils
from manager_utils import pruned_spec_string

import spack.cmd.install
import spack.environment as ev
import spack.main
import spack.util.executable
import spack.util.spack_yaml as syaml
from spack.spec import Spec
from spack.version import GitVersion

git = spack.util.executable.which("git")

add = spack.main.SpackCommand("add")
concretize = spack.main.SpackCommand("concretize")
module = spack.main.SpackCommand("module")


def spack_install_cmd(args=[]):
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


def find_latest_git_hash(spec):
    """
    if the concrete spec's version is using a git branch
    find the latest sha for the branch
    otherwise return None
    """
    branch = sutils.get_version_paired_git_branch(spec)
    if branch:
        # get the matching entry and shas for github
        query = (
            git("ls-remote", "-h", spec.package.git, branch, output=str, error=str)
            .strip()
            .split("\n")
        )
        try:
            assert len(query) == 1
        except Exception:
            print("Too many hits for the remote branch:", spec.name, query)
            exit()

        sha, _ = query[0].split("\t")

        return sha
    else:
        return None


def replace_versions_with_hashes(spec_string, hash_dict):
    """
    given a spec string and a dictionary with the git sha's that have been computed
    replace the spec versions with the git ref versions using the commit sha's
    """
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


def use_latest_git_hashes(env):
    """
    loops over the spec's in the environment and replaces any versions that are based
    on git branches with a specific commit using the version format
    `@git.[hash]=[original concretized version]
    """
    with open(env.manifest_path, "r") as f:
        yaml = syaml.load(f)

    roots = list(env.roots())

    for i in range(len(roots)):
        hash_dict = {}
        hash_dict[roots[i].name] = find_latest_git_hash(roots[i])

        for dep in roots[i].dependencies():
            hash_dict[dep.name] = find_latest_git_hash(dep)

        yaml["spack"]["specs"][i] = replace_versions_with_hashes(roots[i].build_spec, hash_dict)

    with open(env.manifest_path, "w") as fout:
        syaml.dump_config(yaml, stream=fout, default_flow_style=False)
    env._re_read()


def create_snapshots(parser, args):
    """
    Command to create the snapshot environment
    if we use latest git hashes then this will have to concretize twice
    first to create concrete specs so we can loop over the DAG and replace
    versions with git hashes
    and then to concretize after the specs get updated
    """
    snap = sutils.Snapshot(args)
    snap.get_top_level_specs()

    if not args.regular_versions:
        use_latest_git_hashes(snap.env)

        ev.activate(snap.env)
        sutils.command(concretize, "-f")
    if args.install:
        spack_install_cmd()

    return snap.env_path


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "snapshot",
        help="create a timestamped snapshot environment for registered machines.  The install tree"
        " will be held in the environment location to preserve the builds over time and the "
        "installed packages will not be visible to the rest of the spack database outside the "
        "environment.",
    )
    sub_parser.add_argument(
        "--regular_versions",
        "-r",
        action="store_true",
        required=False,
        help="don't replace branch version with latest git hashes as verions",
    )
    sub_parser.add_argument(
        "--name",
        "-n",
        required=False,
        help="name the environment something other than the " "date",
    )
    sub_parser.add_argument(
        "--use_machine_name",
        "-m",
        action="store_true",
        help="use machine name in the snapshot path " "instead of computed architecture",
    )
    sub_parser.add_argument(
        "-s",
        "--specs",
        required=True,
        default=[],
        nargs="+",
        help="Specs to create snapshots for",
    )
    sub_parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        required=False,
        help="install the environment as part of this command rather than as a separate step.  "
        "Depfile installs are generally prefered over using this option",
    )
    command_dict["snapshot"] = create_snapshots
