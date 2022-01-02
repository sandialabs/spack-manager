#!/usr/bin/env spack-python
"""
This script will create the snapshots we need for the exawind project
and any associated modules
"""

import argparse
import os
import sys
from manager_cmds.find_machine import find_machine

import spack.environment as ev
import spack.main
import spack.util.spack_yaml as syaml

from datetime import date

arch = spack.main.SpackCommand('arch')
manager = spack.main.SpackCommand('manager')
add = spack.main.SpackCommand('add')
uninstall = spack.main.SpackCommand('uninstall')
concertize = spack.main.SpackCommand('concretize')
install = spack.main.SpackCommand('install')

base_spec = 'exawind+hypre+openfast'


class SnapshotSpec:
    def __init__(self, id='host-only', spec=base_spec):
        self.id = id
        self.spec = spec


# a list of specs to build in the snapshot, 1 view will be created for each
machine_specs = {
    'darwin': [SnapshotSpec(spec='exawind')],
    'ascicgpu': [SnapshotSpec(),
                 SnapshotSpec(
                     id='cuda',
                     spec=base_spec + '+cuda+amr_wind_gpu+nalu_wind_gpu'
                     ' cuda_arch=70')],
}


def parse(stream):
    parser = argparse.ArgumentParser(
        'create a timestamped snapshot for a Exawind machines')
    parser.add_argument(
        '-m', '--modules', action='store_true',
        help="create modules to associate with each view in the environment")
    parser.add_argument(
        '--just-setup', action='store_true',
        help='only create the environment, don\'t concretize or install')
    parser.set_defaults(modules=False, just_setup=False)

    return parser.parse_args(stream)


def path_extension():
    return "exawind/snapshots/{arch}/{date}".format(
        date=date.today().strftime("%Y%m%d"),
        arch=arch('-t').strip())


def view_excludes(spec):
    if '+cuda' in spec:
        return ['+rocm', '~cuda']
    elif '+rocm' in spec:
        return ['~rocm', '+cuda']
    else:
        return ['+rocm', '+cuda']


def add_spec(env, extension, data, create_modules):
    ev.activate(env)
    add(data.spec)
    ev.deactivate()
    view_path = os.path.join(
        os.environ['SPACK_MANAGER'], 'views', extension, data.id)
    view_dict = {data.id: {
        'root': view_path, 'exclude': view_excludes(data.spec),
        'link_type': 'hard'
    }}
    with open(env.manifest_path, 'r') as f:
        yaml = syaml.load(f)
    # view yaml entry can also be a bool so first try to add to a dictionary,
    # and if that fails overwrite entry as a dictionary
    try:
        yaml['spack']['view'].update(view_dict)
    except AttributeError:
        yaml['spack']['view'] = view_dict

    with open(env.manifest_path, 'w') as f:
        syaml.dump(yaml, stream=f, default_flow_style=False)


def add_develop_specs(env, develop_blacklist=['cmake', 'yaml-cpp']):
    # we have to concretize to solve the dependency tree to extract
    # the top level dependencies and make them develop specs.
    # anything that is not a develop spec is not gauranteed to get installed
    # since spack can reuse them for matching hashes

    print('Setting up develop specs')
    env.concretize()
    dev_specs = set()
    for root in env.roots():
        dev_specs.add(root.format('{name}{@version}'))
        for dep in root.dependencies():
            if dep.name not in develop_blacklist:
                dev_specs.add(dep.format('{name}{@version}'))

    print(dev_specs, len(dev_specs))
    ev.activate(env)
    for spec_string in dev_specs:
        print('spack manager develop ' + spec_string)
        manager('develop', spec_string)
    ev.deactivate()


def create_snapshots(args):
    machine = find_machine(verbose=False)
    extension = path_extension()
    env_path = os.path.join(
        os.environ['SPACK_MANAGER'], 'environments', extension)

    print('Creating snapshot environment')
    manager('create-env', '-d', env_path)
    e = ev.Environment(env_path)
    with e.write_transaction():
        e.yaml['spack']['concretization'] = 'separately'
        e.write()

    # update the spack.yaml in memory so we down't have to carry
    # unnecessary templates for each machine

    spec_data = machine_specs[machine]

    for s in spec_data:
        add_spec(e, extension, s, args.modules)

    add_develop_specs(e)
    if args.just_setup:
        return

    ev.activate(e)
    #concrete_specs = e.concretize(force=True)
    #ev.display_specs(concrete_specs)
    concertize('-f')
    install()


if __name__ == '__main__':
    args = parse(sys.argv[1:])
    create_snapshots(args)
