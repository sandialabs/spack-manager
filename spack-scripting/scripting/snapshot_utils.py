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
import os
from manager_utils import path_extension, pruned_spec_string
from manager_cmds.find_machine import find_machine

import spack.environment as ev
import spack.main
import spack.util.spack_yaml as syaml
from spack.version import GitVersion, Version

manager = spack.main.SpackCommand('manager')
add = spack.main.SpackCommand('add')
concretize = spack.main.SpackCommand('concretize')
module = spack.main.SpackCommand('module')

def command(command, *args):
    """
    Execute a spack.main.SpackCommand uniformly
    and add some print statements
    """
    print('spack', command.command_name, *args)
    print(command(*args, fail_on_error=False))


class Snapshot:

    def __init__(self, args):
        """
        generate the base environment that will be used to create the snapshot
        this will be appended throughout the setup process
        """
        self.args = args
        self.machine = find_machine(verbose=False)
        self.extension = path_extension(args.name, args.use_machine_name)
        self.env_path = os.path.join(
            os.environ['SPACK_MANAGER'], 'environments', self.extension)

        print('\nCreating snapshot environment')

        command(manager, 'create-env', '-d', self.env_path)

        self.env = ev.Environment(self.env_path)

        # TODO refactor this to be a part of create-env command
        with self.env.write_transaction():
            self.env.yaml['spack']['concretizer'] = {'unify': args.unify}
            # keep over writing specs so we don't keep appending them if we call multiple times
            self.env.yaml['spack']['specs'] = args.specs
            self.env.write()


    def add_view_dict(self):
        view_dict = {}
        view_name = 'snapshot'
        view_path = os.path.join(
            os.environ['SPACK_MANAGER'], 'views', self.extension, view_name)
        view_dict = {view_name: {
            'root': view_path,
            'projections': {'all': '{compiler.name}-{compiler.version}/{name}/'
                            '{version}-{hash:4}',
                            '^cuda': '{compiler.name}-{compiler.version}-'
                            '{^cuda.name}-{^cuda.version}/{name}/{version}'
                            '-{hash:4}',
                            '^rocm': '{compiler.name}-{compiler.version}-'
                            '{^rocm.name}-{^rocm.version}/{name}/{version}'
                            '-{hash:4}'},
            'link_type': self.args.link_type,
            'link': 'roots',

        }}
        module_path = os.path.join(
            os.environ['SPACK_MANAGER'], 'modules')
        module_dict = {view_name: {
            'enable': ['tcl'],
            'use_view': view_name,
            'prefix_inspections': {'bin': ['PATH']},
            'roots': {'tcl': module_path},
            'arch_folder': False,
            'tcl':
                  {'projections': {
                  'all': '%s/{compiler.name}/{compiler.version}/{name}-{hash:4}' % self.extension,
                  '^cuda': '%s/{compiler.name}/{compiler.version}/{^cuda.name}/{^cuda.version}/{name}-{hash:4}' % self.extension,
                  '^rocm': '%s/{compiler.name}/{compiler.version}/{^rocm.name}/{^rocm.version}/{name}-{hash:4}' % self.extension,
                  },
                  'hash_length': 0,
        }}}
        with open(self.env.manifest_path, 'r') as f:
            yaml = syaml.load(f)
        # override whatever is there for views with the new information
        yaml['spack']['view'] = view_dict
        yaml['spack']['modules'] = module_dict
        with open(self.env.manifest_path, 'w') as f:
            syaml.dump(yaml, stream=f, default_flow_style=False)



    def get_top_level_specs(self):
        ev.activate(self.env)
        print('\nInitial concretize')
        command(concretize, '-f')
        top_specs = []
        for root in self.env.roots():
            if get_version_paired_git_branch(root):
                top_specs.append(root)
                for dep in root.dependencies():
                    if get_version_paired_git_branch(dep):
                        top_specs.append(dep)
        # remove any duplicates
        self.top_specs = list(dict.fromkeys(top_specs))
        print('\nTop Level Specs:', *[s.name for s in self.top_specs])
        ev.deactivate()

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
            print("Skipping {s}@{v} since this version is no longer valid and is likely from"
                      " --reuse. If this is not desired then please add a version constraint to the spec".format(s=spec.name, v=spec.version))
            return None
    if 'branch' in version_dict.keys():
        return version_dict['branch']
    else:
        return None



