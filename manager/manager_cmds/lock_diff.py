# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.


import os
import random
import string
import sys

import llnl.util.tty as tty

import spack.environment as ev
from spack.spec import Spec

command_name = "lock-diff"
description = "compare two lock files to determine differences in the concrete environments"
aliases = ["ld"]


def setup_parser_args(subparser):
    subparser.add_argument("--old", "-o", help="path to the older spack.lock", required=True)
    subparser.add_argument(
        "--new", "-n", help="path to the newer/updated spack.lock", required=True
    )
    subparser.add_argument(
        "--skip-package-diffs",
        "-s",
        nargs="+",
        default=[],
        help="packages to skip package hash diffs",
        required=False,
    )


def lock_diff(parser, args):
    file_bad = False
    if not os.path.isfile(args.old):
        tty.error(f"{args.old} lock files is not a valid file")
        file_bad = True
    if not os.path.isfile(args.new):
        tty.error(f"{args.new} lock files is not a valid file")
        file_bad = True
    if file_bad:
        sys.exit(1)

    # create randomly named env's
    def generate_random_name(num_chars=10, valid_chars=string.ascii_lowercase):
        return "".join(random.choice(valid_chars) for _ in range(num_chars))

    e_old_name = generate_random_name()
    e_new_name = generate_random_name()

    e_old = ev.create(e_old_name, init_file=args.old)
    e_new = ev.create(e_new_name, init_file=args.new)

    # since they are lock files should be a psuedo no-op
    e_old.concretize()
    e_new.concretize()

    # different specs with the same name can be in both env if the hash's change.
    # reduce to a single instance per spec using a dictionary

    spec_differences = {}
    for s in set(e_old.all_specs()) ^ set(e_new.all_specs()):
        spec_differences[s.name] = s

    def keys_of_diffing_dictionary_values(d1, d2):
        """find keys where values differ for two identically keyed dictionaries"""
        assert d1.keys() == d2.keys()
        pre_out = []
        for item in d1.items() ^ d2.items():
            pre_out.append(item[0])
        return set(pre_out)

    def old_vs_new(old_dict, new_dict):
        """extract the differening values of two dictionaries as two separate strings"""
        old = []
        new = []
        for key in keys_of_diffing_dictionary_values(old_dict, new_dict):
            old.append(str(old_dict[key]))
            new.append(str(new_dict[key]))
        return " ".join(old), " ".join(new)

    # loop over different specs and diagnose what has changed
    # kind of hacky check to see if we have acceptable diffs. worth a refactor someday
    unacceptable_changes = False
    if spec_differences:
        print("Differences in Following Specs Detected:")
        for spec in spec_differences.values():
            old_spec = e_old.matching_spec(Spec(spec.name))
            new_spec = e_new.matching_spec(Spec(spec.name))
            diff_msg = "- {}: ".format(spec.name)
            if old_spec and not new_spec:
                diff_msg += "*removed*"
                unacceptable_changes = True
            elif not old_spec and new_spec:
                diff_msg += "*added*"
                unacceptable_changes = True
            elif new_spec.package_hash() != old_spec.package_hash():
                # this will detect when we make changes in spack, or in our repos
                diff_msg += "package hash change - Old: {} New: {}".format(
                    old_spec.package_hash(), new_spec.package_hash()
                )
                if spec.name not in args.skip_package_diffs:
                    unacceptable_changes = True
            else:
                # something else must have changed in concretization that
                # should be avoided if we don't have reuse
                # these are the things that we want to avoid
                # if we get here then there is a more subtle issue
                unacceptable_changes = True
                assert old_spec.dag_hash() != new_spec.dag_hash()
                diff_msg += "DAG hash change: {} {}".format(
                    old_spec.dag_hash(), new_spec.dag_hash()
                )
                # TODO diff versions, compilers, variants, compiler flags in that order
                # and print diagnostics
                if old_spec.compiler != new_spec.compiler:
                    diff_msg += "\n *compiler diff - \n\tOld: {}\n\tNew: {}".format(
                        old_spec.compiler, new_spec.compiler
                    )
                if old_spec.version != new_spec.version:
                    diff_msg += "\n *version diff - \n\tOld: {}\n\tNew: {}".format(
                        old_spec.version, new_spec.version
                    )
                if old_spec.variants != new_spec.variants:
                    # since package hash is the same, varints should be the same too
                    old_vars, new_vars = old_vs_new(old_spec.variants, new_spec.variants)
                    diff_msg += "\n *variants diff - \n\tOld: {}\n\tNew: {}".format(
                        old_vars, new_vars
                    )
                if old_spec.compiler_flags != new_spec.compiler_flags:
                    old_flags, new_flags = str(old_spec.compiler_flags), str(
                        new_spec.compiler_flags
                    )
                    diff_msg += "\n *compiler_flags diff -\n\tOld {}\n\tNew: {}".format(
                        old_flags, new_flags
                    )
            print(diff_msg)
    else:
        print("Environments are exactly the same")

    # cleanup artifacts
    e_old.destroy()
    e_new.destroy()
    if spec_differences and unacceptable_changes:
        sys.exit(1)
    else:
        sys.exit(0)


def add_command(parser, command_dict):
    subparser = parser.add_parser(
        command_name, description=description, help=description, aliases=aliases
    )
    setup_parser_args(subparser)
    command_dict[command_name] = lock_diff
    for alias in aliases:
        command_dict[alias] = lock_diff
