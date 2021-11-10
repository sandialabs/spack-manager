import sys

import manager_cmds.create_env
import manager_cmds.develop
import manager_cmds.find_machine

if sys.version_info[0] < 3:
    print('spack-manager commands only support python 3')
    exit(1)

description = "commands that are specific to spack-manager"
section = "spack-manager"
level = "short"

_subcommands = {}


def setup_parser(subparser):
    sp = subparser.add_subparsers(metavar='spack-manager commands',
                                  dest='manager_command')
    manager_cmds.create_env.add_command(sp, _subcommands)
    manager_cmds.develop.add_command(sp, _subcommands)
    manager_cmds.find_machine.add_command(sp, _subcommands)


def manager(parser, args):
    _subcommands[args.manager_command](parser, args)
