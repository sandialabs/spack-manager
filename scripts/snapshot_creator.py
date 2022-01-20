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
concretize = spack.main.SpackCommand('concretize')
install = spack.main.SpackCommand('install')
module = spack.main.SpackCommand('module')

base_spec = 'exawind+hypre+openfast'

blacklist = ['cuda', 'cmake', 'yaml-cpp', 'rocm', 'llvm-admgpu', 'hip', 'py-']


def command(command, *args):
    """
    Execute a spack.main.SpackCommand uniformly
    and add some print statements
    """
    print('spack', command.command_name, *args)
    print(command(*args, fail_on_error=True))


class SnapshotSpec:
    """
    Data structure for storing a tag that is not a hash
    to represent the spec added to the spack.yaml
    """
    def __init__(self, id='default', spec=base_spec):
        self.id = id
        self.spec = spec


# a list of specs to build in the snapshot, 1 view will be created for each
machine_specs = {
    'darwin': [SnapshotSpec()],
    'rhodes': [SnapshotSpec()],
    'snl-hpc': [SnapshotSpec()],
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
    phases = ['create_env', 'mod_specs', 'concretize', 'install']
    parser.add_argument(
        '--stop_after', '-sa', choices=phases,
        help='stop script after this phase')
    parser.add_argument('--use_develop', '-ud', action='store_true',
                        help='use develop specs for roots and their immediate '
                             'dependencies')
    parser.add_argument('--name', '-n', required=False,
                        help='naem the environment something other than the '
                        'date')
    parser.set_defaults(modules=False, use_develop=False, stop_after='install')

    return parser.parse_args(stream)


def path_extension(name):
    return "exawind/snapshots/{arch}/{date}".format(
        date=name if name else date.today().strftime("%Y%m%d"),
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
    excludes = view_excludes(data.spec)
    view_path = os.path.join(
        os.environ['SPACK_MANAGER'], 'views', extension, data.id)
    view_dict = {data.id: {
        'root': view_path, 'exclude': excludes,
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

    if create_modules:
        # we want cmake in the view, but not a module
        module_excludes = excludes.copy().append('cmake')
        module_path = os.path.join(
            os.environ['SPACK_MANAGER'], 'modules')
        module_dict = {data.id: {
            'enable': ['tcl'],
            'use_view': data.id,
            'prefix_inspections': {'bin': ['PATH']},
            'roots': {'tcl': module_path},
            'arch_folder': False,
            'tcl': {'projections': {
                    'all': '%s/{name}-%s' % (extension, data.id)},
                    'hash_length': 0,
                    'blacklist_implicits': True,
                    'blacklist': module_excludes}
        }}
        try:
            yaml['spack']['modules'].update(module_dict)
        except KeyError:
            yaml['spack']['modules'] = module_dict

    with open(env.manifest_path, 'w') as f:
        syaml.dump(yaml, stream=f, default_flow_style=False)


def get_top_level_specs(env, blacklist=blacklist):
    env.concretize()
    top_specs = []
    for root in env.roots():
        if root.name in blacklist:
            continue
        top_specs.append(root)
        for dep in root.dependencies():
            if dep.name not in blacklist:
                top_specs.append(dep)
    # remove any duplicates
    top_specs = list(dict.fromkeys(top_specs))
    print('Top Level Specs:', [s.name for s in top_specs])
    return top_specs


def find_latest_git_hash(spec):
    version_dict = spec.package_class.versions[spec.version]
    keys = version_dict.keys()

    if 'branch' in keys:
        # git branch
        ref = 'refs/heads/%s' % version_dict['branch']
    elif 'tag' in keys:
        # already matched
        return None
    elif 'sha256' in keys:
        # already matched
        return None
    else:
        raise Exception(
            'no known git type for ' + spec.format(
                '//{hash} ({name}{@version})'))

    # get the matching entry and shas for github
    query = git('ls-remote', spec.package.git, ref,
                output=str, error=str).strip().split('\n')
    assert len(query) == 1

    sha, _ = query[0].split('\t')

    return sha


def replace_versions_with_hashes(spec_string, hash_dict):
    specs = str(spec_string).strip().split(' ^')
    new_specs = []
    for spec in specs:
        base, rest = spec.split('%')
        name, version = base.split('@')
        hash = hash_dict.get(name)
        if hash:
            version = hash
            new_specs.append('{n}@{v}%{r}'.format(n=name,
                                              v=version, r=rest))
    final = ' ^'.join(new_specs)
    assert '\n' not in final
    assert '\t' not in final
    return final


def use_latest_git_hashes(env, top_specs, blacklist=blacklist):
    with open(env.manifest_path, 'r') as f:
        yaml = syaml.load(f)

    roots = list(env.roots())

    for i in range(len(roots)):
        if roots[i].name not in blacklist:
            hash_dict = {}
            hash_dict[roots[i].name] = find_latest_git_hash(roots[i])

            for dep in roots[i].dependencies():
                if dep.name not in blacklist:
                    hash_dict[dep.name] = find_latest_git_hash(dep)

            yaml['spack']['specs'][i] = replace_versions_with_hashes(
                roots[i].build_spec, hash_dict)

    with open(env.manifest_path, 'w') as fout:
        syaml.dump_config(yaml, stream=fout,
                          default_flow_style=False)
    env._re_read()


def use_develop_specs(env, specs):
    # we have to concretize to solve the dependency tree to extract
    # the top level dependencies and make them develop specs.
    # anything that is not a develop spec is not gauranteed to get installed
    # since spack can reuse them for matching hashes

    print('Setting up develop specs')
    dev_specs = list(dict.fromkeys(
        [s.format('{name}{@version}') for s in specs]))

    ev.activate(env)
    for spec_string in dev_specs:
        # special treatment for trilinos since its clone fails
        # with standard spack develop
        if 'trilinos' in spec_string:
            branch = spec_string.split('@')[-1]
            command(manager, 'develop', '-rb',
                    'https://github.com/trilinos/trilinos',
                    branch, spec_string)
        else:
            command(manager, 'develop', spec_string)
    ev.deactivate()


def create_snapshots(args):
    machine = find_machine(verbose=False)
    extension = path_extension(args.name)
    env_path = os.path.join(
        os.environ['SPACK_MANAGER'], 'environments', extension)

    print('Creating snapshot environment')
    # we add cmake so it is a root spec that will get added to the view
    # so people using the snapshot don't have to rebuild
    command(manager, 'create-env', '-d', env_path, '-s', 'cmake')
    e = ev.Environment(env_path)
    with e.write_transaction():
        e.yaml['spack']['concretization'] = 'separately'
        e.write()

    spec_data = machine_specs[machine]

    for s in spec_data:
        add_spec(e, extension, s, args.modules)

    top_specs = get_top_level_specs(e)

    if args.stop_after == 'create_env':
        return

    if args.use_develop:
        use_develop_specs(e, top_specs)
    else:
        use_latest_git_hashes(e, top_specs)

    if args.stop_after == 'mod_specs':
        return

    ev.activate(e)
    print('Concretize')
    command(concretize, '-f')
    if args.stop_after == 'concretize':
        return
    print('Install')
    command(install)
    if args.modules:
        print('Generate module files')
        command(module, 'tcl', 'refresh', '-y')


if __name__ == '__main__':
    args = parse(sys.argv[1:])
    create_snapshots(args)
