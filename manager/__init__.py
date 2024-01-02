# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import llnl.util.filesystem as fs

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


def initialize():
    """ "
    Function to setup spack-manager data structures in memory.
    This needs to be refined further
    """
    populate_config()


initialize()
