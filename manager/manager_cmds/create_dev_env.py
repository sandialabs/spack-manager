# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import argparse

import spack.cmd
import spack.environment as ev

from . import create_env
from . import develop as mdevelop


def develop(*args):
    """
    wrapper around manager.develop
    """
    parser = argparse.ArgumentParser("develop")
    sub_parser = parser.add_subparsers()
    mdevelop.add_command(sub_parser, {})
    args = parser.parse_args(["develop", *args])
    mdevelop.manager_develop(parser, args)


def create_dev_env(parser, args):
    env_path = create_env.create_env(parser, args)
    env = ev.Environment(env_path)
    ev.activate(env)
    specs = spack.cmd.parse_specs(args.spec)
    for s in specs:
        # check that all specs were concrete
        version = s.versions.concrete_range_as_version
        if not version:
            print(
                "\nWarning: {spec} is not concrete and will not "
                "be setup as a develop spec."
                "\nAll specs must be concrete for "
                "'spack manager create-dev-env' to clone for you i.e. at "
                "least [package]@[version].\nTo learn what versions are"
                " available type 'spack info [package]'"
                "\nSome common exawind versions are: exawind@master, "
                "amr-wind@main and nalu-wind@master\n".format(spec=s)
            )
            continue
        # need to assign version since the concrete property has changed
        s.versions = spack.version.VersionList([version])

        dev_args = []
        yaml = env.manifest.yaml_content
        # kind of hacky, but spack will try to re-clone
        # if we don't give the --path argument even though
        # it is already in the spack.yaml
        if env.is_develop(s) and "path" in yaml["spack"]["develop"][str(s.name)]:
            # keep pointing to the original path that is provided in the spack.yaml
            dev_args.extend(["--path", yaml["spack"]["develop"][str(s.name)]["path"]])
        dev_args.append(str(s.format("{name}{@version}")))
        develop(*dev_args)
    ev.deactivate()


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "create-dev-env",
        help="create a developer focused environment where all root specs are"
        " develop specs and they are automatically cloned from the default"
        " branches",
    )
    create_env.setup_parser_args(sub_parser)
    command_dict["create-dev-env"] = create_dev_env
