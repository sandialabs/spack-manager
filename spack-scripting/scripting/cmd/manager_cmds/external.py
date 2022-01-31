import os
from datetime import datetime
from manager_utils import base_extension
import re
import sys

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
            'Please contact system admins and spack-manager maintainers to sort this out')

    if os.path.isdir(external_arch):
        external = external_arch
    else:
        external = external_machine

    print(external)
    if os.path.isdir(external):
        return external
    else:
        return None


def get_latest_dated_snapshot():
    """
    Get the path for the latest snapshot created by snapshot_creator.py
    based on the name/date created (not necessarily file creation date)
    """
    base_dir = get_external_dir()
    if not base_dir:
        # if no snapshots have been created the directory may not exist
        return
    # get environment directories, make sure we're only pulling in directories
    snapshots = [s for s in os.listdir(base_dir)
                 if os.path.isdir(os.path.join(base_dir, s))]
    print(snapshots)
    # remove anything that isn't a date stamp i.e. (custom snapshots)
    dates = [d for d in snapshots if re.search(r'\d{4}-\d{2}-\d{2}', d)]
    print(dates)
    dates.sort(reverse=True, key=lambda date: datetime.strptime(date, "%Y-%m-%d"))
    return os.path.join(base_dir, dates[0])


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
    env = ev.active_environment()
    if not env:
        tty.die('spack manager external requires an active environment')
    if args.latest:
        snap_path = get_latest_dated_snapshot()
        if not snap_path:
            sys.stderr.write('WARNING: No \'externals.yaml\' created because no valid '
                             'snapshots were found. \n'
                             '\tIf you are trying to use a system level snapshot make '
                             'sure you have SPACK_MANAGER_EXTERNAL pointing to '
                             'spack-manager directory for the system.\n')
            return
    else:
        snap_path = args.path

    # check that directory of ext view exists
    if not ev.is_env_dir(snap_path):
        tty.die('path must point to a spack environment')

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


def add_command(parser, command_dict):
    ext = parser.add_parser('external',
                            help='tools for configuring precompiled'
                            ' binaries', conflict_handler='resolve')

    ext.add_argument('-n',
                     '--name', required=False,
                     help='name the new include file for the '
                     'externals with this name')

    ext.add_argument('-v', '--view', required=False, default='default',
                     help='name of view to use in the environment')

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

    ext.set_defaults(merge=False, view='default',
                     name='externals.yaml', latest=False)

    command_dict['external'] = external
