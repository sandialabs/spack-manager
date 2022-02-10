import os
import re
from datetime import datetime

from manager_utils import base_extension

import llnl.util.tty as tty

import spack.config
import spack.environment as ev
import spack.util.spack_yaml as syaml
from spack.environment import config_dict


def get_external_dir():
    if 'SPACK_MANAGER_EXTERNAL' in os.environ:
        manager_root = os.environ['SPACK_MANAGER_EXTERNAL']
    else:
        manager_root = os.environ['SPACK_MANAGER']
    external_machine = os.path.join(
        manager_root, 'environments', base_extension(True))
    external_arch = os.path.join(
        manager_root, 'environments', base_extension(False))

    if os.path.isdir(external_machine) and os.path.isdir(external_arch):
        raise Exception(
            'ERROR: Snapshots based on arch and machine are both valid. '
            'Please contact system admins and spack-manager maintainers'
            ' to sort this out')

    if os.path.isdir(external_arch):
        external = external_arch
    else:
        external = external_machine

    if os.path.isdir(external):
        return external
    else:
        return None


def get_all_snapshots():
    base_dir = get_external_dir()
    if not base_dir:
        # if no snapshots have been created the directory may not exist
        return
    # get environment directories, make sure we're only pulling in directories
    snapshots = [s for s in os.listdir(base_dir)
                 if os.path.isdir(os.path.join(base_dir, s))]
    return snapshots


def get_latest_dated_snapshot():
    """
    Get the path for the latest snapshot created by snapshot_creator.py
    based on the name/date created (not necessarily file creation date)
    """
    snapshots = get_all_snapshots()
    base_dir = get_external_dir()
    # remove anything that isn't a date stamp i.e. (custom snapshots)
    if base_dir and snapshots:
        dates = [d for d in snapshots if re.search(r'\d{4}-\d{2}-\d{2}', d)]
        dates.sort(reverse=True, key=lambda date: datetime.strptime(
            date, "%Y-%m-%d"))
        return os.path.join(base_dir, dates[0])
    else:
        return


def include_entry_exists(env, name):
    includes = config_dict(env.yaml).get('include', [])
    for entry in includes:
        if entry == name:
            return True
    return False


def add_include_entry(env, inc, prepend=True):
    include = config_dict(env.yaml).get('include', [])
    if len(include) == 0:
        # includes is missing, need to add it
        env.yaml['spack'].insert(0, 'include', [])
        include = config_dict(env.yaml).get('include', [])
    if prepend:
        include.insert(0, inc)
    else:
        include.append(inc)
    env.write()


def write_spec(view, spec):
    template = """  {name}:
    externals:
    - spec: {short_spec}
      prefix: {prefix}
    buildable: false\n"""

    return template.format(
        name=spec.name,
        short_spec=spec.format(
            '{name}{@version}{%compiler}{variants}{arch=architecture}'),
        prefix=view.get_projection_for_spec(spec))


def create_external_yaml_from_env(path, view_key, black_list, white_list):
    active_env = ev.active_environment()
    env = ev.Environment(path)

    env.check_views()
    if view_key is None:
        # get the first view that was added to the environment as the default
        view_key = list(env.views.keys())[0]

    try:
        view = env.views[view_key]
    except KeyError:
        # not sure why I can't find SpackEnvironmentViewError from the module
        raise ev.SpackEnvironmentError(
            'Requested view %s does not exist in %s' % (view_key, path))

    view_specs = [s for s in env._get_environment_specs()
                  if view.__contains__(s)]
    data = "packages:\n"

    for s in view_specs:
        if black_list:
            if s.name in black_list:
                continue
            else:
                data += write_spec(view, s)
        elif white_list:
            if s.name in white_list:
                data += write_spec(view, s)
        else:
            # auto blacklist all develops specs in the env
            # externaling a dev spec will always be an error
            if not active_env.is_develop(s):
                data += write_spec(view, s)
    return syaml.load_config(data)


def external(parser, args):
    if args.list:
        extern_dir = get_external_dir()
        snaps = get_all_snapshots()
        print('Available snapshot directories (and views) are: ')
        for s in snaps:
            env_dir = os.path.join(extern_dir, s)
            env = ev.Environment(env_dir)
            views = ', '.join(env.views.keys())
            print(' - {path} ({views})'.format(path=env_dir, views=views))
        return
    env = ev.active_environment()
    if not env:
        tty.die('spack manager external requires an active environment')
    if args.latest:
        snap_path = get_latest_dated_snapshot()
        if not snap_path:
            print('WARNING: No \'externals.yaml\' created because no valid '
                  'snapshots were found. \n'
                  '  If you are trying to use a system level snapshot make '
                  'sure you have SPACK_MANAGER_EXTERNAL pointing to '
                  'spack-manager directory for the system.\n')
            return
    else:
        snap_path = args.path

    # check that directory of ext view exists
    if not snap_path or not ev.is_env_dir(snap_path):
        tty.die('External path must point to a spack environment with a view. '
                'Auto detection of the latest dated snapshot can be achived'
                ' with the \'--latest\' flag.')

    # copy the file and overwrite any that may exist (or merge?)
    inc_name_abs = os.path.abspath(os.path.join(env.path, args.name))

    try:
        src = create_external_yaml_from_env(
            snap_path, args.view, args.blacklist, args.whitelist)
    except ev.SpackEnvironmentError as e:
        tty.die(e.long_message)

    if include_entry_exists(env, args.name):
        if args.merge:
            # merge the existing includes with the new one
            # giving precedent to the new data coming in
            dest = spack.config.read_config_file(
                inc_name_abs, spack.config.section_schemas['packages'])
            combined = spack.config.merge_yaml(src, dest)
            final = combined
        else:
            final = src
    else:
        add_include_entry(env, args.name)
        final = src

    with open(inc_name_abs, 'w') as fout:
        syaml.dump_config(final, stream=fout,
                          default_flow_style=False)

    # for now we have to use the original concretizer
    # see: https://github.com/spack/spack/issues/28201
    # do this last so we only change the concretizer if we created an external.yaml
    env.yaml['spack']['config'] = {'concretizer': 'original'}
    env.write()


def add_command(parser, command_dict):
    ext = parser.add_parser('external',
                            help='tools for configuring precompiled'
                            ' binaries', conflict_handler='resolve')

    ext.add_argument('-n',
                     '--name', required=False,
                     help='name the new include file for the '
                     'externals with this name')
    ext.add_argument('-v', '--view', required=False,
                     help='name of view to use in the environment.\n'
                     'This will default to the first view in the environment\n'
                     'i.e. the first view listed in "spack manager external --list"'
                     ' command')
    ext.add_argument('-m', '--merge', required=False,
                     action='store_true', help='merge existing yaml files '
                     'together')

    select = ext.add_mutually_exclusive_group()

    select.add_argument('-w',
                        '--whitelist', nargs='*', required=False,
                        help='(not implemeted) specs that should '
                        'be added (omit all others)')
    select.add_argument('-b',
                        '--blacklist', nargs='*', required=False,
                        help='(not implemented) specs that should '
                        'be omitted (add all others)')
    ext.add_argument('path', nargs='?',
                     help='The location of the external install '
                     'directory')
    ext.add_argument('--latest', action='store_true',
                     help='use the latest snapshot available')
    ext.add_argument('--list', action='store_true',
                     help='print a list of the available externals to use.\n'
                     'Values in parenthesis are the view names for each '
                     'external')
    ext.set_defaults(merge=False,
                     name='externals.yaml', latest=False, list=False)

    command_dict['external'] = external
