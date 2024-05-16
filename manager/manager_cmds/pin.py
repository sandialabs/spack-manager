# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

"""
Functions for snapshot creation that are added here to be testable
"""
import llnl.util.tty as tty

import spack.main
import spack.traverse as traverse
import spack.util.executable
from spack.spec import Spec
from spack.version import GitVersion

try:
    from spack.version.common import COMMIT_VERSION
except ImportError:
    from spack.version import COMMIT_VERSION

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
        version = spec.version.ref_version
        version_dict = {}
        version_dict = spec.package_class.versions[version]
    else:
        try:
            version_dict = spec.package_class.versions[spec.version]
        except KeyError:
            tty.warn(
                f"Skipping {spec.name}@{spec.version} since this version is no longer valid "
                "and is likely from --reuse. If this is not desired then please add a "
                "version constraint to the spec"
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
        tty.debug(f"{spec.name} has paired to git branch {branch}")
        # get the matching entry and shas for github
        query = (
            git("ls-remote", "-h", spec.package.git, branch, output=str, error=str).strip().split()
        )
        sha = [hunk for hunk in query if bool(COMMIT_VERSION.match(hunk))]
        try:
            assert len(sha) == 1
        except Exception:
            tty.die("Too many hits for the remote branch:", spec.name, query)

        return sha[0]
    else:
        return None


def spec_string_with_git_ref_for_version(spec):
    """
    if a spec is using a git branch for the version replace the version with sha of latest commit
    """
    if not spec.concrete:
        tty.warn(
            f"Skipping {spec.name} because it is not concrete. "
            "Reconcretize to include in pin analysis"
        )
        return
    # create string representation of the spec and break it into parts
    if isinstance(spec.version, GitVersion):
        version_str = str(spec.version.ref_version)
    else:
        version_str = spec.format("{version}")
    # get hash
    sha = find_latest_git_hash(spec)
    if sha:
        version_str = "git.{h}={v}".format(h=sha, v=version_str)
        new_spec_str = f"{spec.name}@{version_str}"
        tty.debug(f"Pin: Reformatting {spec.name} to {new_spec_str}")
        return new_spec_str
    else:
        return None


def pin_graph(root, pinRoot=True, pinDeps=True):
    updated_spec = ""
    new_root = ""
    new_deps = ""
    if pinRoot:
        new_root = spec_string_with_git_ref_for_version(root)
    if pinDeps:
        for dep in traverse.traverse_nodes([root], root=False):
            pinned_dep = spec_string_with_git_ref_for_version(dep)
            if pinned_dep:
                new_deps += f" ^{pinned_dep}"
    if new_root:
        updated_spec = new_root
        if new_deps:
            updated_spec += new_deps
    elif new_deps:
        updated_spec = root.name + new_deps
    if updated_spec:
        tty.debug(f"Pin: Generating new root spec - {updated_spec}")
        return Spec(updated_spec)


def pin_env(parser, args):
    """
    pin versions paired to git branches with latest sha
    requires concrete specs to work so we must concretize once before looping over
    the dag, and then once after we replace the versions to make sure the environment
    still concretizes
    """
    env = spack.cmd.require_active_env(cmd_name="pin")
    cargs = ["--force"]

    if args.fresh:
        cargs.append("--fresh")

    tty.debug("Pin: Pinning branches to sha's")
    pinRoot = args.roots or args.all
    pinDeps = args.dependencies or args.all
    for user, root in env.concretized_specs():
        new_root = pin_graph(root, pinRoot, pinDeps)
        if new_root:
            with env.write_transaction():
                env.change_existing_spec(change_spec=new_root, match_spec=user)

    tty.debug("Pin: Reconcretizing with updated specs")
    concretize(*cargs)


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
        "-a", "--all", action="store_true", default=True, help="pin all specs in the DAG"
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
