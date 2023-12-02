# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

"""
A script for creating a new environment
on a given machine
"""

import os
import sys

import llnl.util.tty as tty

import spack
import spack.cmd
import spack.environment.environment as environment
import spack.extensions.manager as manager
from spack.extensions.manager.environment_utils import SpackManagerEnvironmentManifest
from spack.extensions.manager.manager_cmds.find_machine import find_machine, machine_defined
from spack.extensions.manager.manager_cmds.includes_creator import IncludesCreator


def create_env(parser, args):
    if args.directory is not None:
        if os.path.exists(args.directory) is False:
            print("making", args.directory)
            os.makedirs(args.directory)

        theDir = args.directory
    elif args.name is not None:
        theDir = os.path.join(os.environ["SPACK_MANAGER"], "environments", args.name)
        if os.path.exists(theDir) is False:
            print("making", theDir)
            os.makedirs(theDir)
    else:
        theDir = os.getcwd()

    if args.yaml:
        assert os.path.isfile(args.yaml)
        environment.create_in_dir(theDir, init_file=args.yaml, keep_relative=True)
    else:
        environment.create_in_dir(theDir, init_file=args.yaml, keep_relative=True, with_view=False)

    manifest = SpackManagerEnvironmentManifest(theDir)

    if not args.yaml:
        manifest.set_config_value("concretizer", "unify", True)

    msg = (
        "Specified machine {m} was not found. "
        "To see registered machines run `spack manager find-machine --list`"
    )
    if args.machine is not None:
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

    if args.spec:
        spec_list = spack.cmd.parse_specs(args.spec)
        for s in spec_list:
            manifest.add_user_spec(str(s))

    if args.local_source:
        manifest.set_config_value("config", "install_tree", {"root": "$env/opt"})

    # the machine is not found we take the first/default project
    if not project:
        _, project = list(manager.projects.values())[0]

    # if no projects are configured then there will be zero includes
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

        include_file_name = "include.yaml"
        include_file = os.path.join(theDir, include_file_name)
        inc_creator.write_includes(include_file)
        manifest.append_includes(include_file_name)
    manifest.flush()

    fpath = os.path.join(project.root, ".tmp")

    os.makedirs(fpath, exist_ok=True)

    storage = os.path.join(fpath, "created_env_path.txt")

    with open(storage, "w") as f:
        f.write(theDir)

    return theDir


def setup_parser_args(sub_parser):
    sub_parser.add_argument("-m", "--machine", required=False, help="Machine to match configs")
    name_group = sub_parser.add_mutually_exclusive_group()
    name_group.add_argument("-d", "--directory", required=False, help="Directory to copy files")
    name_group.add_argument(
        "-n",
        "--name",
        required=False,
        help="Name of directory to copy files that will be in " r"{PROJECT}/environments",
    )
    sub_parser.add_argument(
        "-y", "--yaml", required=False, help="Reference spack.yaml to copy to directory"
    )
    sub_parser.add_argument(
        "-s",
        "--spec",
        required=False,
        default=[],
        nargs="+",
        help="Specs to populate the environment with",
    )
    sub_parser.add_argument(
        "-l",
        "--local-source",
        action="store_true",
        required=False,
        help="Move install tree inside the environment directory. This will divorce all the "
        "installations from the rest of the spack database",
    )


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "create-env", help="convenience script" " for setting up a spack environment"
    )
    setup_parser_args(sub_parser)
    command_dict["create-env"] = create_env
