#! /usr/bin/env spack-python
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

import argparse
import os

import snapshot_creator

import spack.environment as ev
import spack.main

manager = spack.main.SpackCommand("manager")
concretize = spack.main.SpackCommand("concretize")
config = spack.main.SpackCommand("config")
snapshot = spack.main.SpackCommand("snapshot")
install = spack.main.SpackCommand("install")

# set up the snapshot
print("Create Snapshot")
snapshot("--install", "-n", "test", "-s", "exawind+hypre+openfast")
location = os.path.join(os.environ["SPACK_MANAGER"], "snapshots", "exawind", "test")

# set up the user environment
print("Create user environment")
env_path = os.path.join(os.environ["SPACK_MANAGER"], "environments", args.dev_name)
command(manager, "create-env", "--directory", env_path, "--spec", "nalu-wind")
ev.activate(ev.Environment(env_path))
command(manager, "external", "--blacklist", "nalu-wind", location)
command(manager, "develop", "nalu-wind@master")
command(concretize)
command(install)
