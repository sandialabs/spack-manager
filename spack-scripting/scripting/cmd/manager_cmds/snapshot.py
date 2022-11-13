# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
import argparse

import snapshot_utils as sutils

import spack.cmd.install
import spack.environment as ev
import spack.main
import spack.util.spack_yaml as syaml

add = spack.main.SpackCommand("add")
concretize = spack.main.SpackCommand("concretize")
module = spack.main.SpackCommand("module")


def spack_install_cmd(args=[]):
    """
    manually call spack.install so we get output
    """
    parser = argparse.ArgumentParser("dummy parser")
    # this is missing from the parser but not really used so we create a dummy
    parser.add_argument("--not_used", dest="verbose", required=False)
    spack.cmd.install.setup_parser(parser)
    parsed_args = parser.parse_args(args)
    print(parsed_args)
    spack.cmd.install.install(parser, parsed_args)


def use_latest_git_hashes(env):
    """
    loops over the spec's in the environment and replaces any versions that are based
    on git branches with a specific commit using the version format
    `@git.[hash]=[original concretized version]
    """
    with open(env.manifest_path, "r") as f:
        yaml = syaml.load(f)

    roots = list(env.roots())

    for i, root in enumerate(roots):
        spec_str = sutils.spec_string_with_git_ref_for_version(root)
        for dep in root.dependencies():
            spec_str += " ^{0}".format(sutils.spec_string_with_git_ref_for_version(dep))

        yaml["spack"]["specs"][i] = spec_str

    with open(env.manifest_path, "w") as fout:
        syaml.dump_config(yaml, stream=fout, default_flow_style=False)
    env._re_read()


def create_snapshots(parser, args):
    """
    Command to create the snapshot environment
    if we use latest git hashes then this will have to concretize twice
    first to create concrete specs so we can loop over the DAG and replace
    versions with git hashes
    and then to concretize after the specs get updated
    """
    snap = sutils.Snapshot(args)
    snap.get_top_level_specs()

    if not args.regular_versions:
        use_latest_git_hashes(snap.env)

        ev.activate(snap.env)
        sutils.command(concretize, "-f")
    if args.install:
        spack_install_cmd()

    return snap.env_path


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "snapshot",
        help="create a timestamped snapshot environment for registered machines.  The install tree"
        " will be held in the environment location to preserve the builds over time and the "
        "installed packages will not be visible to the rest of the spack database outside the "
        "environment.",
    )
    sub_parser.add_argument(
        "--regular_versions",
        "-r",
        action="store_true",
        required=False,
        help="don't replace branch version with latest git hashes as verions",
    )
    sub_parser.add_argument(
        "--name",
        "-n",
        required=False,
        help="name the environment something other than the " "date",
    )
    sub_parser.add_argument(
        "--use_machine_name",
        "-m",
        action="store_true",
        help="use machine name in the snapshot path " "instead of computed architecture",
    )
    sub_parser.add_argument(
        "-s",
        "--specs",
        required=True,
        default=[],
        nargs="+",
        help="Specs to create snapshots for",
    )
    sub_parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        required=False,
        help="install the environment as part of this command rather than as a separate step.  "
        "Depfile installs are generally prefered over using this option",
    )
    command_dict["snapshot"] = create_snapshots
