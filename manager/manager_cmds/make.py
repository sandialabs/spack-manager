# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import spack.build_environment as build_environment
import spack.builder
import spack.cmd
try:
    import spack.llnl.util.tty as tty
    from spack.llnl.util.filesystem import working_dir
except ImportError:
    import llnl.util.tty as tty
    from llnl.util.filesystem import working_dir
import spack.paths
from spack.util.executable import Executable

"""
This was originally implemented by Tim Fuller @tjfulle
With his permission it is being published in the spack manager
subset of commands
"""
description = "make SPEC directly with `make` or `ninja`"
section = "manager"
level = "short"


def setup_parser(parser):
    parser.add_argument(
        "spec", metavar="SPEC", nargs="+", help="Spack package to build (must be a develop spec)"
    )
    build_args = parser.add_mutually_exclusive_group()
    build_args.add_argument(
        "--args",
        "-a",
        default="",
        required=False,
        help="Additional arguments to pass to make as a string i.e. `--args='test -j16'`",
    )
    build_args.add_argument(
        "-j",
        type=int,
        required=False,
        help="number of ranks to build with (specialized implementation of --args)",
    )


def make(parser, args):
    env = spack.cmd.require_active_env(cmd_name="make")
    specs = spack.cmd.parse_specs(args.spec)
    if args.j:
        extra_make_args = [f"-j{args.j}"]
    else:
        extra_make_args = args.args.split()
    if not specs:
        tty.die("You must supply a spec.")
    if len(specs) != 1:
        tty.die("Too many specs.  Supply only one.")
    spec = env.matching_spec(specs[0])
    if spec is None:
        tty.die(f"{specs[0]}: spec not found in environment")
    elif not spec.is_develop:
        tty.die(f"{specs[0]}: must be a develop spec")
    pkg = spec.package
    builder = spack.builder.create(pkg)
    if hasattr(builder, "build_directory"):
        build_directory = os.path.normpath(os.path.join(pkg.stage.path, builder.build_directory))
    else:
        build_directory = pkg.stage.source_path
    try:
        build_environment.setup_package(spec.package, False, "build")
    except TypeError:
        build_environment.setup_package(spec.package, False)

    if not os.path.isdir(build_directory):
        tty.die(
            (
                "Build directory does not exist. "
                "Please run `spack install` to ensure the build is "
                "configured properly"
            )
        )

    with working_dir(build_directory):
        make_program = "ninja" if os.path.exists("build.ninja") else "make"
        make = Executable(make_program)
        make(*extra_make_args)


def add_command(parser, command_dict):
    subparser = parser.add_parser("make", help=description)
    setup_parser(subparser)
    command_dict["make"] = make
