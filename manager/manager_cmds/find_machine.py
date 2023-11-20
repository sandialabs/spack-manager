# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os
import socket
import sys
import manager


def find_machine(parser, args, verbose=True, full_machine_name=False):
    if args.list:
        print("Project:\t Machine:\t Detectable: (+/-)")
        print("-"*60)
        for name, project in manager.projects.items():
            for m_name, m_detector in project.machines.items():
                print("{proj} \t {machine} \t {detectable}".format(proj=name, machine=m_name, detectable="+" if m_detector else "-"))
        return

    for project in manager.projects:
        for machine_name, data in project.machines.items():
            """
            Since we don't expect uniform environments on all machines
            we bury our checks in a try/except
            """
            try:
                if data.i_am_this_machine():
                    if verbose:
                        print(machine_name)
                    if full_machine_name:
                        return data.full_machine_name
                    else:
                        return machine_name
            except KeyError:
                """
                expect key errors when an environment variable is not defined
                so these are skipped
                """
                pass
            except Exception:
                """
                all other errors will be raised and kill the program
                we can add more excpetions to the pass list as needed
                in the future
                """
                raise
            if verbose:
                print("NOT-FOUND")
            return "NOT-FOUND"

def setup_parser_args(sub_parser):
    sub_parser.add_argument("-l",
                            "--list",
                            action="store_true",
                            required=False,
                            help="list the machines that are preconfigured in spack-manager"
    )

def add_command(parser, command_dict):
    sub_parser = parser.add_parser("find-machine", help="get the current machine detected by spack-manager")
    setup_parser_args(sub_parser)
    command_dict["find-machine"] = find_machine
