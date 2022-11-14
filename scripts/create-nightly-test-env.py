#!/usr/bin/env spack-python
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

import argparse
import sys

import spack.environment as env
import spack.main

manager = spack.main.SpackCommand("manager")
add_spec = spack.main.SpackCommand("add")


def parse(args):
    parser = argparse.ArgumentParser("Create nightly test environments")
    parser.add_argument("-d", "--directory", required=True, help="directory to create file")
    parser.add_argument("-test-nalu", dest="test_nalu", action="store_true", help="test nalu")
    parser.add_argument("-nalu-wind-vars", help="string of spack variants for nalu-wind")
    parser.set_defaults(test_nalu=False)
    return parser.parse_args(args)


def variant_factory(spec_string):
    if "nalu-wind" in spec_string:
        add_spec("trilinos")
        branch = "master" if "triilinos@master" in spec_string else "develop"
        print("cloning trilinos {b}".format(b=branch))
        manager(
            "develop",
            "-rb",
            "https://github.com/trilinos/trilinos",
            branch,
            "trilinos@{b}".format(b=branch),
        )

    if "+openfast" in spec_string:
        add_spec("openfast")
        print("cloning openfast")
        manager("develop", "openfast@master")

    if "+hypre" in spec_string:
        add_spec("hypre")
        print("cloning hypre")
        manager("develop", "hypre@develop")

    if "+tioga" in spec_string:
        add_spec("tioga")
        print("cloning tioga")
        manager("develop", "tioga@develop")


def create_test_env(args):
    if args.test_nalu:
        manager(
            "create-env", "-d", args.directory, "-s", "nalu-wind-nightly" + args.nalu_wind_vars
        )
        with env.Environment(args.directory):
            test_package = "nalu-wind-nightly@master"
            spec = test_package + args.nalu_wind_vars
            variant_factory(spec)
            print("cloning nalu-wind")
            manager(
                "develop", "-rb", "https://github.com/Exawind/nalu-wind", "master", test_package
            )


if __name__ == "__main__":
    args = parse(sys.argv[1:])
    create_test_env(args)
    # we could potentially just run the enviornment install after this
    # the catch is our test environments would capture changes in spack-manager
    # this could be good or bad depending on how you look at testing
