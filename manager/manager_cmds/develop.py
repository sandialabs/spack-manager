# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os
import shutil

import llnl.util.tty as tty

import spack.cmd
import spack.util.executable
from spack.cmd.develop import develop as s_develop
from spack.cmd.develop import setup_parser as s_setup_parser
from spack.error import SpackError
from spack.extensions.manager.manager_utils import canonicalize_path


def git_clone(branch, repo, path, shallow, all_branches):
    """
    git clone wrapper to help with mocking
    """
    git = spack.util.executable.which("git")
    git_args = ["clone", "--recursive"]
    if not all_branches:
        git_args.append("--single-branch")
    if shallow:
        git_args.extend(["--depth", "1"])
    git_args.extend(["--branch", branch, repo, path])
    git(*git_args)


def git_remote_add(path, name, repo):
    """
    git remote add wrapper
    """
    git = spack.util.executable.which("git")
    git("-C", path, "remote", "add", name, repo)


def _redundant_code_from_spack_develop(args):
    """
    Re-use the path and spec checking from spack.cmd.develop
    https://github.com/spack/spack/blob/b56f464c29c3e316c3afbbde52bf2597ad5351f1/lib/spack/spack/cmd/develop.py#L65-L95
    """
    env = spack.cmd.require_active_env(cmd_name="develop")

    if not args.spec:
        if args.clone is False:
            raise SpackError("No spec provided to spack develop command")

        # download all dev specs
        for name, entry in env.dev_specs.items():
            path = entry.get("path", name)
            abspath = canonicalize_path(path, default_wd=env.path)

            if os.path.exists(abspath):
                msg = "Skipping developer download of %s" % entry["spec"]
                msg += " because its path already exists."
                tty.msg(msg)
                continue

            # Both old syntax `spack develop pkg@x` and new syntax `spack develop pkg@=x`
            # are currently supported.
            spec = spack.spec.parse_with_version_concrete(entry["spec"])
            pkg_cls = spack.repo.path.get_pkg_class(spec.name)
            pkg_cls(spec).stage.steal_source(abspath)

        if not env.dev_specs:
            tty.warn("No develop specs to download")

        return

    specs = spack.cmd.parse_specs(args.spec)
    if len(specs) > 1:
        raise SpackError("spack develop requires at most one named spec")

    spec = specs[0]
    version = spec.versions.concrete_range_as_version
    if not version:
        raise SpackError("Packages to develop must have a concrete version")

    spec.versions = spack.version.VersionList([version])

    # default path is relative path to spec.name
    path = args.path or spec.name
    abspath = canonicalize_path(path, default_wd=env.path)

    # clone default: only if the path doesn't exist
    clone = args.clone
    if clone is None:
        clone = not os.path.exists(abspath)

    if not clone and not os.path.exists(abspath):
        raise SpackError("Provided path %s does not exist" % abspath)

    if clone and os.path.exists(abspath):
        if args.force:
            shutil.rmtree(abspath)
        else:
            msg = "Path %s already exists and cannot be cloned to." % abspath
            msg += " Use `spack develop -f` to overwrite."
            raise SpackError(msg)
    return (clone, abspath)


def manager_develop(parser, args):
    """
    gives the option to clone based on specific fork and branch
    """

    clone, path = _redundant_code_from_spack_develop(args)

    if args.repo_branch and clone:
        repo, branch = args.repo_branch
        git_clone(branch, repo, path, args.shallow, args.all_branches)
        args.clone = False

    s_develop(None, args)

    if args.add_remote:
        # a clone must have taken place at this point so we can
        # safely add a repo
        remote_name, remote_repo = args.add_remote
        git_remote_add(path, remote_name, remote_repo)


def add_command(parser, command_dict):
    subparser = parser.add_parser(
        "develop",
        help="a more intuitieve interface for " "spack develop",
        conflict_handler="resolve",
    )
    s_setup_parser(subparser)
    clone_group = subparser.add_mutually_exclusive_group()
    clone_group.add_argument(
        "-rb",
        "--repo-branch",
        nargs=2,
        metavar=("repo", "branch"),
        required=False,
        help="git repo to clone from",
    )
    subparser.add_argument(
        "--shallow",
        required=False,
        action="store_true",
        help="performa a shallow clone of the repo",
    )
    subparser.add_argument(
        "--all-branches",
        required=False,
        action="store_true",
        help="clone all branches " "of the repo",
        default=False,
    )
    subparser.add_argument(
        "--add-remote",
        nargs=2,
        metavar=("remote_name", "remote_repo"),
        required=False,
        help="add a remote as part of the clone",
    )

    command_dict["develop"] = manager_develop
