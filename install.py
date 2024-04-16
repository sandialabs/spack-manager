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
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("check", os.path.join(os.path.dirname(sys.argv[0]), "check.py"))
check = importlib.util.module_from_spec(spec)
sys.modules["check"] = check
spec.loader.exec_module(check)

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--scope", required=False, help="Spack scope to register spack-manager")
parser.add_argument("--test", action='store_true', help="Don't actually install but test installation process")

if __name__ == "__main__":
    args = parser.parse_args()
    check.check_spack_manager_requirements()

    extension_path = os.path.realpath(os.getcwd())
    if not os.path.isdir(os.path.join(extension_path, "manager")):
        tty.die("Spack-Manager installation script must be run from inside the source directory")

    register_args = []

    if args.scope:
        register_args.extend(["--scope", args.scope])

    register_args.extend(["add", "config:extensions:[{0}]".format(extension_path)])

    if args.test:
        print("TEST:: config", *register_args)
    else:
        config = spack.main.SpackCommand("config")
        config(*register_args)
