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
import spack.util.executable

from datetime import date

git = spack.util.executable.which('git')

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
        'create a timestamped snapshot for registered machines')
    parser.add_argument(
        '-m', '--modules', action='store_true',
        help='create modules to associate with each view in the environment')
    phases = ['create_env', 'develop', 'concretize', 'install']
    parser.add_argument(
        '--stop_after', '-sa', choices=phases,
        help='stop script after this phase')
    parser.add_argument('--use_develop', '-ud', action='store_true',
                        help='use develop specs for roots and their immediate dependencies')
    parser.set_defaults(modules=False, use_develop=False, stop_after='install')

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


def get_top_level_specs(env, blacklist=['cmake', 'yaml-cpp']):
    env.concretize()
    top_specs = set()
    for root in env.roots():
        if root.name in blacklist:
            continue
        top_specs.add(root.format('{name}{@version}'))
        for dep in root.dependencies():
            if dep.name not in blacklist:
                top_specs.add(dep.format('{name}{@version}'))
    return top_specs


def find_latest_git_hash(env, spec_name):
    spec = env.matching_spec(spec_name)
    version_dict = spec.package_class.version[spec.version]
    keys = version_dict.keys()

    if 'branch' in keys:
        # git branch
        ref = 'refs/heads/%s' % version_dict['branch']
    elif 'tag' in keys:
        ref = 'refs/tags/%s' % version_dict['tag']
    elif 'sha256' in keys:
        # already matched
        return version_dict['sha256']

    # get all the entries and shas for github
    query = git('ls-remote', spec.package.git, ref,
                output=str, error=str).strip().split('\n')
    assert len(query) == 1

    sha, _ = query[0].split('\t')
    return sha


def add_develop_specs(env):
    # we have to concretize to solve the dependency tree to extract
    # the top level dependencies and make them develop specs.
    # anything that is not a develop spec is not gauranteed to get installed
    # since spack can reuse them for matching hashes

    print('Setting up develop specs')
    dev_specs = get_top_level_specs(env)

    print(dev_specs, len(dev_specs))
    ev.activate(env)
    for spec_string in dev_specs:
        print('spack manager develop ' + spec_string)
        # special treatment for trilinos since if fails with standard spack develop
        if 'trilinos' in spec_string:
            branch = spec_string.split('@')[-1]
            manager('develop', '-rb',
                    'https://github.com/trilinos/trilinos', branch, spec_string)
        else:
            manager('develop', spec_string)
    ev.deactivate()


def create_snapshots(args):
    machine = find_machine(verbose=False)
    extension = path_extension()
    env_path = os.path.join(
        os.environ['SPACK_MANAGER'], 'environments', extension)

    print('Creating snapshot environment')
    # we add cmake so it is a root spec that will get added to the view
    # so people using the snapshot don't have to rebuild
    manager('create-env', '-d', env_path, '-s', 'cmake')
    e = ev.Environment(env_path)
    with e.write_transaction():
        e.yaml['spack']['concretization'] = 'separately'
        e.write()

    spec_data = machine_specs[machine]

    for s in spec_data:
        add_spec(e, extension, s, args.modules)
    if args.stop_after == 'create_env':
        return

    if args.use_develop:
        add_develop_specs(e)

    if args.stop_after == 'develop':
        return

    ev.activate(e)
    print('Concretize')
    concrete_specs = e.concretize(force=True)
    ev.display_specs(concrete_specs)
    # concertize('-f')
    if args.stop_after == 'concretize':
        return
    print('Install')
    install('-v')


if __name__ == '__main__':
    args = parse(sys.argv[1:])
    create_snapshots(args)
