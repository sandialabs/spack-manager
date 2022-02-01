import os
import shutil

import spack.cmd
import spack.cmd.develop as spack_develop
import spack.util.executable
from spack.error import SpackError


def git_clone(branch, repo, path, shallow):
    """
    git clone wrapper to help with mocking
    """
    git = spack.util.executable.which('git')
    git_args = ['clone', '--single-branch', '--recursive']
    if shallow:
        git_args.extend(['--depth', '1'])
    git_args.extend(['--branch', branch, repo, path])
    git(*git_args)


def _redundant_code_from_spack_develop(args):
    """
    Re-use the path and spec checking from spack.cmd.develop
    https://github.com/spack/spack/blob/b56f464c29c3e316c3afbbde52bf2597ad5351f1/lib/spack/spack/cmd/develop.py#L65-L95
    """
    env = spack.cmd.require_active_env(cmd_name='develop')

    specs = spack.cmd.parse_specs(args.spec)
    if len(specs) > 1:
        raise SpackError("spack develop requires at most one named spec")

    spec = specs[0]
    if not spec.versions.concrete:
        raise SpackError("Packages to develop must have a concrete version")

    spec = specs[0]
    if not spec.versions.concrete:
        raise SpackError("Packages to develop must have a concrete version")

    # default path is relative path to spec.name
    path = args.path or spec.name

    # get absolute path to check
    abspath = path
    if not os.path.isabs(abspath):
        abspath = os.path.join(env.path, path)

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
        git_clone(branch, repo, path, args.shallow)
        args.clone = False

    spack_develop.develop(None, args)


def add_command(parser, command_dict):
    subparser = parser.add_parser('develop', help='a more intuitieve interface for '
                                  'spack develop', conflict_handler='resolve')
    spack_develop.setup_parser(subparser)
    clone_group = subparser.add_mutually_exclusive_group()
    clone_group.add_argument('-rb', '--repo-branch', nargs=2,
                             metavar=('repo', 'branch'), required=False,
                             help='git repo to clone from')
    subparser.add_argument('--shallow', required=False, action='store_true',
                           help='performa a shallow clone of the repo')

    command_dict['develop'] = manager_develop
