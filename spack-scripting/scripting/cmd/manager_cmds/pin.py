# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

"""
Functions for snapshot creation that are added here to be testable
"""
from manager_utils import command, pruned_spec_string

import llnl.util.tty as tty

import spack.environment as ev
import spack.main
import spack.traverse as traverse
import spack.util.executable
from spack.version import GitVersion, Version

git = spack.util.executable.which("git")
concretize = spack.main.SpackCommand("concretize")


def get_version_paired_git_branch(spec):
    """
    get the branch that is associate with a spack version if it exists
    else return None
    """
    if isinstance(spec.version, GitVersion):
        # if it is already a GitVersion then we've probably already ran this
        # once we are going to recreate the paried version that the git hash
        # has been assigned to and use that
        version = Version(spec.version.ref_version_str)
        version_dict = spec.package_class.versions[version]
    else:
        try:
            version_dict = spec.package_class.versions[spec.version]
        except KeyError:
            print(
                "Skipping {s}@{v} since this version is no longer valid and is likely from"
                " --reuse. If this is not desired then please add a version constraint to "
                "the spec".format(s=spec.name, v=spec.version)
            )
            return None
    if "branch" in version_dict.keys():
        return version_dict["branch"]
    else:
        return None


def find_latest_git_hash(spec):
    """
    if the concrete spec's version is using a git branch
    find the latest sha for the branch
    otherwise return None
    """
    branch = get_version_paired_git_branch(spec)
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


def spec_string_with_git_ref_for_version(spec):
    """
    if a spec is using a git branch for the version replace the version with sha of latest commit
    """
    # create string representation of the spec and break it into parts
    spec_str = str(spec).strip().split(" ^")[0]
    base, rest = spec_str.split("%")
    name, version = base.split("@")
    if isinstance(spec.version, GitVersion):
        version_str = spec.version.ref_version_str
    else:
        version_str = spec.format("{version}")
    # get hash
    sha = find_latest_git_hash(spec)
    if sha:
        version_str = "git.{h}={v}".format(h=sha, v=version_str)
        return pruned_spec_string("{n}@{v}%{r}".format(n=name, v=version_str, r=rest))
    else:
        return None


def pin_graph(root, pinRoot=True, pinDeps=True):
    if pinRoot:
        spec_str = spec_string_with_git_ref_for_version(root)
    else:
        spec_str = pruned_spec_string(str(root).strip().split(" ^")[0])
    if pinDeps:
        for dep in traverse.traverse_nodes([root], root=False):
            test_spec = spec_string_with_git_ref_for_version(dep)
            if test_spec:
                spec_str += " ^{0}".format(test_spec)
    return spec_str


def pin_env(parser, args):
    """
    pin versions paired to git branches with latest sha
    requires concrete specs to work so we must concretize once before looping over
    the dag, and then once after we replace the versions to make sure the environment
    still concretizes
    """
    env = ev.active_environment()
    if not env:
        tty.die("spack manager pin requires an active environment")
    manifest = env.manifest

    cargs = ["--force"]

    if args.fresh:
        cargs.append("--fresh")

    print("Concretizing environment to resolve DAG")
    command(concretize, *cargs)

    roots = list(env.roots())

    print("Pinning branches to sha's")
    pinRoot = args.root or args.all
    pinDeps = args.dependencies or args.all
    for i, root in enumerate(roots):
        spec_str = pin_graph(root, pinRoot, pinDeps)
        if spec_str:
            manifest.override_user_spec(spec_str, i)

    print("Updating the spack.yaml")
    manifest.flush()
    env._re_read()

    print("Reconcretizing with updated specs")
    command(concretize, *cargs)


def setup_parser_args(sub_parser):
    spec_types = sub_parser.add_mutually_exclusive_group()
    spec_types.add_argument(
        "-r", "--roots", action="store_true", default=False, help="only pin root spec versions"
    )
    spec_types.add_argument(
        "-d",
        "--dependencies",
        action="store_true",
        default=False,
        help="only pin root spec dependencie versions",
    )
    spec_types.add_argument(
        "-a", "--all", action="store_true", default=False, help="pin all specs in the DAG"
    )
    sub_parser.add_argument(
        "--fresh",
        "-f",
        action="store_true",
        default=False,
        help="use --fresh during the concretization process",
    )


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "pin",
        help="pin git branch versions in the active environment's DAG to"
        " the current git commits. This requires concretization twice.",
    )
    setup_parser_args(sub_parser)
    command_dict["pin"] = pin_env
