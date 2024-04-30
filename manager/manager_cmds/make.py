# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import argparse
import os

import llnl.util.tty as tty
import spack.build_environment as build_environment
import spack.builder
import spack.cmd
import spack.paths
from llnl.util.filesystem import working_dir
from spack.util.executable import Executable

"""
This was originally implemented by Tim Fuller @tjfulle
With his permission it is being published in the spack manager 
subset of commands
"""
description = "make SPEC directly with `make` or `ninja`"
section = "manager"
level = "short"

epilog = """\
Additional arguments can be sent to the build system directly by separating them
from SPEC by '--'.  Eg, `spack make SPEC -- -j16`
"""


def setup_parser(parser):
    parser.epilog = epilog
    parser.add_argument(
        "spec",
        metavar="SPEC",
        nargs=argparse.REMAINDER,
        help="Spack package to build (must be a develop spec)",
    )


def make(parser, args):
    env = spack.cmd.require_active_env(cmd_name="make")
    try:
        sep_index = args.spec.index("--")
        extra_make_args = args.spec[sep_index + 1 :]
        specs = args.spec[:sep_index]
    except ValueError:
        extra_make_args = []
        specs = args.spec
    specs = spack.cmd.parse_specs(specs)
    if not specs:
        tty.die("You must supply a spec.")
    if len(specs) != 1:
        tty.die("Too many specs.  Supply only one.")
    spec = env.matching_spec(specs[0])
    if spec is None:
        tty.die(f"{specs[0]}: spec not found in environment")
    pkg = spec.package
    builder = spack.builder.create(pkg)
    if hasattr(builder, "build_directory"):
        build_directory = os.path.normpath(os.path.join(pkg.stage.path, builder.build_directory))
    else:
        build_directory = pkg.stage.source_path
    try:
        build_environment.setup_package(spec.package, False, "build")
    except:
        build_environment.setup_package(spec.package, False)

    if not os.path.isdir(build_directory):
        tty.die(
            "Build directory does not exist. Please run `spack install` to ensure the build is configured properly"
        )

    with working_dir(build_directory):
        make_program = "ninja" if os.path.exists("build.ninja") else "make"
        make = Executable(make_program)
        make(*extra_make_args)


def add_command(parser, command_dict):
    subparser = parser.add_parser("make", help=description)
    setup_parser(subparser)
    command_dict["make"] = make
