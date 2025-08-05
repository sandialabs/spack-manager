# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

from .. import projects as m_proj


def machine_defined(name):
    for project in m_proj.get_projects():
        for machine in project.machines:
            if machine == name:
                return project
    return None


def find_machine(verbose=False, projects=m_proj.get_projects()):
    machine_name = "NOT-FOUND"

    for project in projects:
        for machine in project.machines:
            """
            Since we don't expect uniform environments on all machines
            we bury our checks in a try/except
            """
            try:
                if project.detector(machine):
                    machine_name = machine
                    if verbose:
                        print(project.name, machine_name)
                    return project, machine
            except Exception:
                """
                all  errors will be raised and kill the program
                we can add more excpetions to the pass list as needed
                in the future
                """
                raise

    if verbose:
        print("NONE", machine_name)
    return None, machine_name


def find_machine_cmd(parser, args):
    projects = m_proj.get_projects(args.project)
    if args.list:
        print("Project:\t Machine:\t Detected: (+/-)")
        print("-" * 60)
        for project in projects:
            for machine in project.machines:
                print(
                    "{proj} \t {machine} \t {detected}".format(
                        proj=project.name,
                        machine=machine,
                        detected="+" if project.detector(machine) else "-",
                    )
                )
        return
    elif args.config:
        project, machine = find_machine(verbose=False, projects=projects)
        if not project or machine == "NOT-FOUND":
            return
        else:
            path = os.path.join(project.config_path, machine)
            print(path)
            return path
    else:
        find_machine(verbose=True, projects=projects)


def setup_parser_args(sub_parser):
    sub_parser.add_argument(
        "-p",
        "--project",
        required=False,
        help=(
            "filter results to the project specified. argument can be the name, path or list "
            "index of the project"
        ),
    )
    sub_parser.add_argument(
        "-c",
        "--config",
        action="store_true",
        required=False,
        help="location of the machine specific configs",
    )

    sub_parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        required=False,
        help="list the machines that are preconfigured in spack-manager",
    )


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "find-machine", help="get the current machine detected by spack-manager"
    )
    setup_parser_args(sub_parser)
    command_dict["find-machine"] = find_machine_cmd
