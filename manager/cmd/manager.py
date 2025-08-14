# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details
import sys

from ..manager_cmds import (
    binary_finder,
    cache_query,
    cli_config,
    create_dev_env,
    create_env,
    develop,
    distribution
    external,
    find_machine,
    include,
    location,
    lock_diff,
    make,
    pin,
)

try:
    from .manager_cmds import analyze

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
    distribution.add_command(sp, _subcommands)
    lock_diff.add_command(sp, _subcommands)
    external.add_command(sp, _subcommands)
    find_machine.add_command(sp, _subcommands)
    include.add_command(sp, _subcommands)
    location.add_command(sp, _subcommands)
    pin.add_command(sp, _subcommands)
    make.add_command(sp, _subcommands)


def manager(parser, args):
    _subcommands[args.manager_command](parser, args)
