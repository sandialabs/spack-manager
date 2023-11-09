# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import sys

from scripting.cmd.manager_cmds import create_dev_env
from scripting.cmd.manager_cmds import create_env
from scripting.cmd.manager_cmds import develop
from scripting.cmd.manager_cmds import external
from scripting.cmd.manager_cmds import find_machine
from scripting.cmd.manager_cmds import pin
from scripting.cmd.manager_cmds import snapshot

if sys.version_info[0] < 3:
    # TODO use tty
    print("spack-manager commands only support python 3")
    exit(1)

description = "commands that are specific to spack-manager"
section = "spack-manager"
level = "short"

_subcommands = {}


def setup_parser(subparser):
    sp = subparser.add_subparsers(metavar="spack-manager commands", dest="manager_command")
    create_env.add_command(sp, _subcommands)
    create_dev_env.add_command(sp, _subcommands)
    develop.add_command(sp, _subcommands)
    find_machine.add_command(sp, _subcommands)
    external.add_command(sp, _subcommands)
    pin.add_command(sp, _subcommands)
    snapshot.add_command(sp, _subcommands)


def manager(parser, args):
    _subcommands[args.manager_command](parser, args)
