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

import argparse
import os

import spack
import spack.cmd
import spack.environment.environment as environment
from spack.extensions.manager.environment_utils import SpackManagerEnvironmentManifest
from spack.extensions.manager.manager_cmds.include import include_creator
from spack.extensions.manager.manager_cmds.location import location


def create_env(parser, args):
    if args.name is not None:
        theDir = environment.create(args.name, init_file=args.yaml, keep_relative=True).path
    else:
        if args.directory is not None:
            if os.path.exists(args.directory) is False:
                print("making", args.directory)
                os.makedirs(args.directory)
            theDir = args.directory
        else:
            theDir = os.getcwd()
        environment.create_in_dir(theDir, init_file=args.yaml, keep_relative=True)

    manifest = SpackManagerEnvironmentManifest(theDir)

    if not args.yaml:
        manifest.set_config_value("concretizer", "unify", True)
        manifest.set_config_value("view", False)

    if args.spec:
        spec_list = spack.cmd.parse_specs(args.spec)
        for s in spec_list:
            manifest.add_user_spec(str(s))

    if args.local_source:
        manifest.set_config_value("config", "install_tree", {"root": "$env/opt"})

    # handle includes, if it is not set up right then nothing gets created
    include_dict = {"machine": args.machine, "dir": theDir, "file": "include.yaml"}

    inc_args = argparse.Namespace(**include_dict)
    include_file_name = include_creator(None, inc_args)

    if include_file_name:
        manifest.append_includes(include_file_name)

    manifest.flush()

    fpath = os.path.join(location(), ".tmp")
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
