#! /usr/bin/env spack-python
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
"""
This is the installation script for spack-manager.
It can be called for multiple instances of spack and simply registers
the extension with spack.
"""

import argparse
import llnl.util.tty as tty
import os
import spack.main


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--scope", required=False, help="Spack scope to register spack-manager")

if __name__ == "__main__":
    args = parser.parse_args()

    extension_path = os.path.realpath(os.getcwd())
    if not os.path.isdir(os.path.join(extension_path, "manager")):
        tty.die("Spack-Manager installation script must be run from inside the source directory")

    register_args = []

    if args.scope:
        register_args.extend(["--scope", args.scope])

    register_args.extend(["add", "config:extensions:[{0}]".format(extension_path)])

    config = spack.main.SpackCommand("config")
    config(*register_args)
