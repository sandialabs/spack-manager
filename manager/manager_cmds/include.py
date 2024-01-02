# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os
import sys

import llnl.util.tty as tty

import spack.extensions.manager as manager
import spack.extensions.manager.projects as projects
from spack.extensions.manager.manager_cmds.find_machine import find_machine, machine_defined
from spack.extensions.manager.manager_cmds.includes_creator import IncludesCreator


def include_creator(parser, args):
    include_file = None
    msg = (
        "Specified machine {m} was not found. "
        "To see registered machines run `spack manager find-machine --list`"
    )
    # the machine is not found we take the first/default project
    all_projects = projects.get_projects()
    if args.machine:
        project = machine_defined(args.machine)
        if not project:
            tty.error(msg.format(m=args.machine))
            sys.exit(1)
        else:
            machine = args.machine
    else:
        project, machine = find_machine()
        if machine == "NOT-FOUND":
            tty.warn(msg.format(m=args.machine))

    # the machine is not found we take the first/default project
    if not project and all_projects:
        project = all_projects[0]

    # if no projects are configured then there is nothing to create
    if project:
        inc_creator = IncludesCreator()
        genPath = os.path.join(project.config_path, "base")
        hostPath = os.path.join(project.config_path, machine)
        userPath = os.path.join(project.config_path, "user")

        if os.path.exists(genPath):
            inc_creator.add_scope("base", genPath)

        if os.path.exists(hostPath):
            inc_creator.add_scope("machine", hostPath)

        if os.path.exists(userPath):
            inc_creator.add_scope("sm_user", userPath)

        if args.file:
            include_file = args.file
        else:
            include_file = os.path.join(os.getcwd(), "include.yaml")
        inc_creator.write_includes(include_file)
    return include_file


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "include", help="create machine specific includes files for consistent environments"
    )
    sub_parser.add_argument("-m", "--machine", required=False, help="Machine to match configs")
    sub_parser.add_argument(
        "-f", "--file", required=False, help="Name of the include file to create"
    )
    command_dict["include"] = include_creator
