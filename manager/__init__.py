# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

"""
This module is the top level and deals specifically with manipulating the configuration
file.  The data from the configuration file is then available and immutable to all
other modules.
"""
import os

import llnl.util.filesystem as fs
import llnl.util.tty as tty

import spack.util.spack_yaml as syaml

_default_config = """
spack-manager:
    projects: []
"""

_default_config_path = os.path.realpath(
    os.path.abspath(os.path.join(__file__, "..", "..", "spack-manager.yaml"))
)

config_path = _default_config_path
config_yaml = {}


def populate_config():
    """Update the spack-manager config in memory"""
    global config_yaml
    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            config_yaml = syaml.load(f)
    else:
        with open(config_path, "w") as f:
            f.write(_default_config)
        config_yaml = syaml.load(_default_config)


def write_config():
    global config_yaml
    with fs.write_tmp_and_move(os.path.realpath(config_path)) as f:
        syaml.dump(config_yaml, f)
    populate_config()


class MissingProjectException(Exception):
    pass


def add_project(path):
    global config_yaml
    if path not in config_yaml["spack-manager"]["projects"]:
        config_yaml["spack-manager"]["projects"].insert(0, path)
        write_config()
    else:
        tty.warn("Project is already registered")


def remove_project_via_path(path):
    global config_yaml
    if path in config_yaml["spack-manager"]["projects"]:
        config_yaml["spack-manager"]["projects"].remove(path)
        write_config()
    else:
        raise MissingProjectException("No project is registered with the path {0}".format(path))


def remove_project_via_index(index):
    global config_yaml
    if len(config_yaml["spack-manager"]["projects"]) > abs(index):
        config_yaml["spack-manager"]["projects"].pop(index)
        write_config()
    else:
        breakpoint()
        raise MissingProjectException("No project is registered with the index {0}".format(index))


def initialize():
    """ "
    Function to setup spack-manager data structures in memory.
    This needs to be refined further
    """
    populate_config()


initialize()
