# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import sys

import spack.extensions.manager.manager_cmds.binary_finder as binary_finder
import spack.extensions.manager.manager_cmds.cache_query as cache_query
import spack.extensions.manager.manager_cmds.cli_config as cli_config
import spack.extensions.manager.manager_cmds.create_dev_env as create_dev_env
import spack.extensions.manager.manager_cmds.create_env as create_env
import spack.extensions.manager.manager_cmds.develop as develop
import spack.extensions.manager.manager_cmds.lock_diff as lock_diff
import spack.extensions.manager.manager_cmds.external as external
import spack.extensions.manager.manager_cmds.find_machine as find_machine
import spack.extensions.manager.manager_cmds.include as include
import spack.extensions.manager.manager_cmds.location as location
import spack.extensions.manager.manager_cmds.make as make
import spack.extensions.manager.manager_cmds.pin as pin


if sys.version_info < (3, 8):
    print("spack-manager commands only supported in python 3.8 and higher")
    exit(1)

description = "commands that are specific to spack-manager"
section = "spack-manager"
level = "short"

_subcommands = {}


def setup_parser(subparser):
    sp = subparser.add_subparsers(metavar="spack-manager commands", dest="manager_command")

    cli_config.cli_commands["add"](sp, _subcommands)
    cli_config.cli_commands["remove"](sp, _subcommands)
    cli_config.cli_commands["list"](sp, _subcommands)

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
