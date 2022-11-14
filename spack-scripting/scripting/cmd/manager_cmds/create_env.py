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

import manager_cmds.find_machine as fm
from manager_cmds.find_machine import find_machine
from manager_cmds.includes_creator import IncludesCreator

import spack
import spack.cmd
import spack.environment.environment as environment
import spack.util.spack_yaml as syaml


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

    has_view = False
    if args.yaml:
        assert os.path.isfile(args.yaml)
        with open(args.yaml, "r") as fyaml:
            print(fyaml)
            user_yaml = syaml.load_config(fyaml)
            user_view = environment.config_dict(user_yaml).get("view")
            if user_view:
                has_view = True
    env = environment.Environment(
        theDir, init_file=args.yaml, with_view=has_view, keep_relative=True
    )
    yaml = env.yaml

    def _unify_already_set(yaml):
        return (
            "spack" in yaml
            and "concretizer" in yaml["spack"]
            and "unify" in yaml["spack"]["concretizer"]
        )

    if not args.yaml or not _unify_already_set(yaml):
        yaml["spack"]["concretizer"] = {"unify": True}
        with env.write_transaction():
            env.write()

    if args.machine is not None:
        machine = args.machine
        if machine not in fm.machine_list.keys():
            raise Exception("Specified machine %s is not defined" % machine)
    else:
        machine = find_machine(verbose=False)

    if args.spec:
        spec_list = spack.cmd.parse_specs(args.spec)
        for s in spec_list:
            env.add(s)

    inc_creator = IncludesCreator()
    genPath = os.path.join(os.environ["SPACK_MANAGER"], "configs", "base")
    inc_creator.add_scope("base", genPath)
    hostPath = os.path.join(os.environ["SPACK_MANAGER"], "configs", machine)
    userPath = os.path.join(os.environ["SPACK_MANAGER"], "configs", "user")

    if os.path.exists(hostPath):
        inc_creator.add_scope("machine", hostPath)
    else:
        print("Host not setup in spack-manager: %s" % hostPath)
    if os.path.exists(userPath):
        inc_creator.add_scope("machine", userPath)

    include_file_name = "include.yaml"
    include_file = os.path.join(theDir, include_file_name)
    inc_creator.write_includes(include_file)
    if "include" in yaml["spack"]:
        yaml["spack"]["include"].append(include_file_name)
    else:
        yaml["spack"]["include"] = [include_file_name]

    env.write()

    fpath = os.path.join(os.environ["SPACK_MANAGER"], ".tmp")

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
        help="Name of directory to copy files that will be in " "$SPACK_MANAGER/environments",
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


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "create-env", help="convenience script" " for setting up a spack environment"
    )
    setup_parser_args(sub_parser)
    command_dict["create-env"] = create_env
