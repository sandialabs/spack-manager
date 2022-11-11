#!/usr/bin/env spack-python
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

"""
This script will create the snapshots we need for the exawind project
and any associated modules
"""

import argparse
import os
import sys
import snapshot_utils as sutils
from manager_utils import path_extension, pruned_spec_string

import spack.environment as ev
import spack.main
import spack.util.spack_yaml as syaml
import spack.util.executable
import spack.cmd.install
from spack.spec import Spec
from spack.version import GitVersion, Version



git = spack.util.executable.which('git')

manager = spack.main.SpackCommand('manager')
add = spack.main.SpackCommand('add')
concretize = spack.main.SpackCommand('concretize')
module = spack.main.SpackCommand('module')


def spack_install_cmd(args):
    """
    manually call spack.install so we get output
    """
    parser = argparse.ArgumentParser('dummy parser')
    # this is missing from the parser but not really used so we create a dummy
    parser.add_argument('--not_used', dest='verbose', required=False)
    spack.cmd.install.setup_parser(parser)
    parsed_args = parser.parse_args(args)
    print(parsed_args)
    spack.cmd.install.install(parser, parsed_args)


def parse(stream):
    parser = argparse.ArgumentParser(
        'create a timestamped snapshot for registered machines')
    parser.add_argument(
        '-m', '--modules', action='store_true',
        help='create modules to associate with each view in the environment')
    phases = ['create_env', 'mod_specs', 'concretize', 'install']
    parser.add_argument('--git_hash_version', '-g', default=True,
                        help="replace branch version with latest git hashes as verions")
    parser.add_argument('--name', '-n', required=False,
                        help='name the environment something other than the '
                        'date')
    parser.add_argument('--use_machine_name', '-M', action='store_true',
                        help='use machine name in the snapshot path '
                        'instead of computed architecture')
    parser.add_argument(
        "-s",
        "--specs",
        required=True,
        default=[],
        nargs="+",
        help="Specs to create snapshots for",
    )

    return parser.parse_args(stream)


def find_latest_git_hash(spec):
    branch = sutils.get_version_paired_git_branch(spec)
    if branch:
        # get the matching entry and shas for github
        query = git('ls-remote', spec.package.git, branch,
                    output=str, error=str).strip().split('\n')
        assert len(query) == 1

        sha, _ = query[0].split('\t')

        return sha
    else:
        return None


def replace_versions_with_hashes(spec_string, hash_dict):
    specs = str(spec_string).strip().split(' ^')
    new_specs = []
    for spec in specs:
        base, rest = spec.split('%')
        name, version = base.split('@')

        # use paired version if it is already a GitVersion
        newSpec = Spec(spec)
        if isinstance(newSpec.version, GitVersion):
            version = newSpec.version.ref_version_str

        hash = hash_dict.get(name)
        if hash:
            version = 'git.{hash}={version}'.format(hash=hash, version=version)
            # prune the spec string to get rid of patches which could cause
            # conflicts later
            new_specs.append(pruned_spec_string('{n}@{v}%{r}'.format(n=name,
                                                                     v=version,
                                                                     r=rest)))
    final = ' ^'.join(new_specs)
    assert '\n' not in final
    assert '\t' not in final
    return final


def use_latest_git_hashes(env):
    with open(env.manifest_path, 'r') as f:
        yaml = syaml.load(f)

    roots = list(env.roots())

    for i in range(len(roots)):
            hash_dict = {}
            hash_dict[roots[i].name] = find_latest_git_hash(roots[i])

            for dep in roots[i].dependencies():
                hash_dict[dep.name] = find_latest_git_hash(dep)

            yaml['spack']['specs'][i] = replace_versions_with_hashes(
                roots[i].build_spec, hash_dict)

    with open(env.manifest_path, 'w') as fout:
        syaml.dump_config(yaml, stream=fout,
                          default_flow_style=False)
    env._re_read()


def create_snapshots(args):
    snap = sutils.Snapshot(args)
    snap.get_top_level_specs()

    if args.git_hash_version:
        use_latest_git_hashes(snap.env)

        ev.activate(snap.env)
        sutils.command(concretize, '-f')

    return snap.env_path


if __name__ == '__main__':
    args = parse(sys.argv[1:])
    create_snapshots(args)
