# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

"""
Implementations for interacting and editing the spack-manager YAML config from the
command line interface
"""
import spack.extensions.manager as manager
import spack.extensions.manager.projects as projects


def _impl_add(parser, args):
    manager.add_project(args.project)


def _impl_remove(parser, args):
    """
    remove a project based on index, name, or path
    """

    def remove_name_based(name_or_path):
        # project objects don't exist yet in the manager module
        # so check name here where the objects can be created
        # and remove via list
        for i, p in enumerate(projects.get_projects()):
            if p.name == name_or_path:
                manager.remove_project_via_index(i)
                return
            else:
                # TODO this may require path canonicaliztion?
                manager.remove_project_via_path(name_or_path)
                return

    index = -1e6
    try:
        index = int(args.project)
    except ValueError:
        # bad conversion, not index
        remove_name_based(args.project)
        return
    manager.remove_project_via_index(int(args.project))
    return


def _impl_list(parser, args):
    registry = projects.get_projects()
    print("-" * 15)
    print("Spack-Manager Projects:")
    print("Index:\tName\t\tPath")
    print("-" * 15)
    for i, p in enumerate(registry):
        print("{0}:\t{1}\t{2}".format(i, p, p.root))


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "add", help="register a project in the spack-manager.yaml config file"
    )
    sub_parser.add_argument("project", help="the path to the project being added")

    command_dict["add"] = _impl_add


def list_command(parser, command_dict):
    sub_parser = parser.add_parser("list", help="list the registered projects")

    command_dict["list"] = _impl_list


def remove_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "remove", help="remove a project in the spack-manager.yaml config file"
    )
    sub_parser.add_argument(
        "project",
        help="the project index, name, or path to remove (tried in that order if there are conflicts)",
    )

    command_dict["remove"] = _impl_remove


# dictionary for easy addition of commands
cli_commands = {"add": add_command, "remove": remove_command, "list": list_command}
