#!/usr/bin/env spack-python
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

"""
Functions for snapshot creation that are added here to be testable
"""
import argparse
import os

import manager_cmds.create_env
from manager_cmds.find_machine import find_machine
from manager_utils import path_extension, pruned_spec_string

import spack.environment as ev
import spack.main
import spack.util.executable
from spack.version import GitVersion, Version

git = spack.util.executable.which("git")
add = spack.main.SpackCommand("add")
concretize = spack.main.SpackCommand("concretize")
module = spack.main.SpackCommand("module")


def get_version_paired_git_branch(spec):
    if isinstance(spec.version, GitVersion):
        # if it is already a GitVersion then we've probably already ran this
        # once we are going to recreate the paried version that the git hash
        # has been assigned to and use that
        version = Version(spec.version.ref_version_str)
        version_dict = spec.package_class.versions[version]
    else:
        try:
            version_dict = spec.package_class.versions[spec.version]
        except KeyError:
            print(
                "Skipping {s}@{v} since this version is no longer valid and is likely from"
                " --reuse. If this is not desired then please add a version constraint to "
                "the spec".format(s=spec.name, v=spec.version)
            )
            return None
    if "branch" in version_dict.keys():
        return version_dict["branch"]
    else:
        return None


def find_latest_git_hash(spec):
    """
    if the concrete spec's version is using a git branch
    find the latest sha for the branch
    otherwise return None
    """
    branch = get_version_paired_git_branch(spec)
    if branch:
        # get the matching entry and shas for github
        query = (
            git("ls-remote", "-h", spec.package.git, branch, output=str, error=str)
            .strip()
            .split("\n")
        )
        try:
            assert len(query) == 1
        except Exception:
            print("Too many hits for the remote branch:", spec.name, query)
            exit()

        sha, _ = query[0].split("\t")

        return sha
    else:
        return None


def spec_string_with_git_ref_for_version(spec):
    """
    if a spec is using a git branch for the version replace the version with sha of latest commit
    """
    # create string representation of the spec and break it into parts
    spec_str = str(spec).strip().split(" ^")[0]
    base, rest = spec_str.split("%")
    name, version = base.split("@")
    version_str = spec.format("{version}")
    # get hash
    sha = find_latest_git_hash(spec)
    if sha:
        version_str = "git.{h}={v}".format(h=sha, v=version_str)
    return pruned_spec_string("{n}@{v}%{r}".format(n=name, v=version_str, r=rest))


def command(command, *args):
    """
    Execute a spack.main.SpackCommand uniformly
    and add some print statements
    """
    print("spack", command.command_name, *args)
    print(command(*args, fail_on_error=False))


def env_creation_wrapper(path, specs, template):
    args = ["create-env", "-d", path, "-s", *specs, "-y", template]
    parser = argparse.ArgumentParser("create")
    sub_parser = parser.add_subparsers()
    manager_cmds.create_env.add_command(sub_parser, {})
    args = parser.parse_args([*args])
    manager_cmds.create_env.create_env(parser, args)


class Snapshot:
    def __init__(self, args):
        """
        generate the base environment that will be used to create the snapshot
        this will be appended throughout the setup process
        """
        template = os.path.join(os.environ["SPACK_MANAGER"], "env-templates", "snapshot.yaml")
        self.args = args
        self.machine = find_machine(verbose=False)
        self.extension = path_extension(args.name, args.use_machine_name)
        self.env_path = os.path.join(os.environ["SPACK_MANAGER"], self.extension)

        print("\nCreating snapshot environment")

        yaml_path = os.path.join(self.env_path, "spack.yaml")
        if os.path.isfile(yaml_path):
            os.remove(yaml_path)

        # command(manager, "create-env", "-d", self.env_path, "-s", *args.specs, "-y", template)
        env_creation_wrapper(self.env_path, args.specs, template)

        self.env = ev.Environment(self.env_path)

        with self.env.write_transaction():
            self.env.yaml["spack"]["view"] = True
            lmod = self.env.yaml["spack"]["modules"]["default"]["lmod"]
            lmod["projections"]["all"] = self.extension + "/{name}/{version}"
            lmod["projections"]["^cuda"] = (
                self.extension + "/{^cuda.name}-{^cuda.version}/{name}/{version}"
            )
            lmod["projections"]["^rocm"] = (
                self.extension + "/{^rocm.name}-{^rocm.version}/{name}/{version}"
            )
            self.env.write()

    def get_top_level_specs(self):
        ev.activate(self.env)
        print("\nInitial concretize")
        command(concretize, "-f")
        top_specs = []
        for root in self.env.roots():
            if get_version_paired_git_branch(root):
                top_specs.append(root)
                for dep in root.dependencies():
                    if get_version_paired_git_branch(dep):
                        top_specs.append(dep)
        # remove any duplicates
        self.top_specs = list(dict.fromkeys(top_specs))
        print("\nTop Level Specs:", *[s.name for s in self.top_specs])
        ev.deactivate()
