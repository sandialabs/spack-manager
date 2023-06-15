#! /usr/bin/env spack-python
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

import os

from snapshot_utils import command

import spack.environment as ev
import spack.main

manager = spack.main.SpackCommand("manager")
concretize = spack.main.SpackCommand("concretize")
config = spack.main.SpackCommand("config")
install = spack.main.SpackCommand("install")
# we really need something small with only 1-2 dependencies for testing this out

# set up the snapshot
print("Create Snapshot")
manager("snapshot", "--install", "-n", "snap_test", "-s", "h5z-zfp")
location = os.path.join(os.environ["SPACK_MANAGER"], "snapshots", "exawind", "snap_test")

# set up the user environment
print("Create user environment")
env_path = os.path.join(os.environ["SPACK_MANAGER"], "environments", "dev_test")
command(manager, "create-dev-env", "--directory", env_path, "--spec", "h5z-zfp@develop")
ev.activate(ev.Environment(env_path))
command(install)
