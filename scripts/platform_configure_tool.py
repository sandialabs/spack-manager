#! /usr/bin/env spack-python
import argparse
import os
import pathlib

import spack.main
import spack.util.spack_yaml as syaml

from spack.util.module_cmd import module

parser = argparse.ArgumentParser()
parser.add_argument("input", help="input file describing what to configure")
parser.add_argument("--output", help="location where the configs should get written")

args = parser.parse_args()

input_path = pathlib.PurePath(args.input)
output_path = pathlib.PurePath(args.output)

os.environ["SPACK_USER_CONFIG_PATH"] = str(output_path)
exe_env = os.environ.copy()

with open(input_path, "r") as f:
    manifest = syaml.load(f)

compiler = spack.main.SpackCommand("compiler", subprocess=True)
external_cmd = spack.main.SpackCommand("external", subprocess=True)

if "compilers" in manifest:
    for c in manifest["compilers"]:
        module("load", c)
        print(compiler("find", "--scope=user", env=exe_env))
        module("unload", c)

if "externals" in manifest:
    print(external_cmd("find", *manifest["externals"], env=exe_env))

if "modules" in manifest:
    for entry in manifest["modules"]:
        m = entry["module"]
        p = entry["packages"]
        module("load", m)
        print(external_cmd("find", *p, env=exe_env))
        module("unload", m)
