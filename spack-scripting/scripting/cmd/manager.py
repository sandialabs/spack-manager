import manager_cmds.create_env
import manager_cmds.find_machine

description = "commands that are specific to spack-manager"
section = "spack-manager"
level = "short"

_subcommands = {}


def setup_parser(subparser):
    sp = subparser.add_subparsers(metavar='SUBCOMMAND', dest='manager_command')
    manager_cmds.find_machine.add_command(sp, _subcommands)
    manager_cmds.create_env.add_command(sp, _subcommands)


def manager(parser, args):
    _subcommands[args.manager_command](parser, args)
