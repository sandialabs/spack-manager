# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from ..manager_cmds import binary_finder as binary_finder
from ..manager_cmds import cache_query as cache_query
from ..manager_cmds import cli_config as cli_config
from ..manager_cmds import create_dev_env as create_dev_env
from ..manager_cmds import create_env as create_env
from ..manager_cmds import develop as develop
from ..manager_cmds import external as external
from ..manager_cmds import find_machine as find_machine
from ..manager_cmds import include as include
from ..manager_cmds import location as location
from ..manager_cmds import lock_diff as lock_diff
from ..manager_cmds import make as make
from ..manager_cmds import pin as pin

try:
    from .manager_cmds import analyze as analyze

    _analyze_imports = True
except ImportError:
    _analyze_imports = False


description = "commands that are specific to spack-manager"
section = "spack-manager"
level = "short"

_subcommands = {}


def setup_parser(subparser):
    sp = subparser.add_subparsers(metavar="spack-manager commands", dest="manager_command")

    cli_config.cli_commands["add"](sp, _subcommands)
    cli_config.cli_commands["remove"](sp, _subcommands)
    cli_config.cli_commands["list"](sp, _subcommands)
    if _analyze_imports:
        analyze.add_command(sp, _subcommands)
    binary_finder.add_command(sp, _subcommands)
    cache_query.add_command(sp, _subcommands)
    create_env.add_command(sp, _subcommands)
    create_dev_env.add_command(sp, _subcommands)
    develop.add_command(sp, _subcommands)
    lock_diff.add_command(sp, _subcommands)
    external.add_command(sp, _subcommands)
    find_machine.add_command(sp, _subcommands)
    include.add_command(sp, _subcommands)
    location.add_command(sp, _subcommands)
    pin.add_command(sp, _subcommands)
    make.add_command(sp, _subcommands)


def manager(parser, args):
    _subcommands[args.manager_command](parser, args)
