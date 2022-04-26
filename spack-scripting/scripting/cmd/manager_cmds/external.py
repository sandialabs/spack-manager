import os
import re
from datetime import datetime

from manager_utils import base_extension

import llnl.util.tty as tty

import spack
import spack.config
import spack.detection
import spack.environment as ev
import spack.util.spack_yaml as syaml
from spack.detection.common import _pkg_config_dict
from spack.environment import config_dict
from spack.spec import Spec


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


def get_ordered_dated_snapshots():
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
        return list(dates)
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


def create_external_detected_spec(env, spec):
    view = _get_first_view_containing_spec(env, spec)
    pruned_spec = _well_posed_spec_string_minus_dev_path(spec)
    prefix = view.get_projection_for_spec(spec)
    return spack.detection.DetectedPackage(Spec.from_detection(pruned_spec), prefix)


def assemble_dict_of_detected_externals(env, black_list, white_list):
    external_spec_dict = {}
    active_env = ev.active_environment()

    def update_dictionary(env, spec):
        if spec.name in external_spec_dict:
            external_spec_dict[spec.name].append(
                create_external_detected_spec(env, spec))
        else:
            external_spec_dict[spec.name] = [
                create_external_detected_spec(env, spec)]

    for spec in env.all_specs():
        if black_list:
            if spec.name not in black_list:
                update_dictionary(env, spec)
        elif white_list:
            if spec.name in white_list:
                update_dictionary(env, spec)
        else:
            if not active_env.is_develop(spec):
                update_dictionary(env, spec)
    return external_spec_dict


def create_yaml_from_detected_externals(ext_dict):
    formatted_dict = {}
    for name, entries in ext_dict.items():
        config = _pkg_config_dict(entries)
        config['buildable'] = False
        formatted_dict[name] = config

    return syaml.syaml_dict({'packages': formatted_dict})


def _well_posed_spec_string_minus_dev_path(spec):
    full_spec = spec.format(
        '{name}{@version}{%compiler}{variants}{arch=architecture}')
    spec_components = full_spec.split(' ')
    variants_to_omit = ('dev_path=', 'patches=')

    def filter_func(entry):
        for v in variants_to_omit:
            if v in entry:
                return False
        return True
    pruned_components = list(filter(filter_func, spec_components))

    pruned_spec = ' '.join(pruned_components)
    return pruned_spec


def _get_first_view_containing_spec(env, spec):
    for view in env.views.values():
        if view.__contains__(spec):
            return view
    return None


def external(parser, args):
    extern_dir = get_external_dir()
    if args.list:
        snaps = get_all_snapshots()
        dated = get_ordered_dated_snapshots()
        if snaps and dated:
            non_dated = list(set(snaps) - set(dated))

        def print_snapshots(snaps):
            for s in snaps:
                env_dir = os.path.join(extern_dir, s)
                print(' - {path}'.format(path=env_dir))

        print('-' * 54)
        print('Available snapshot directories are:')
        print('-' * 54)
        if dated:
            print('\nDated Snapshots (ordered)')
            print('-' * 54)
            print_snapshots(dated)
        if non_dated:
            print('\nAdditional Snapshots (unordered)')
            print('-' * 54)
            print_snapshots(non_dated)
        return
    env = ev.active_environment()
    if not env:
        tty.die('spack manager external requires an active environment')
    if args.latest:
        snaps = get_ordered_dated_snapshots()
        if not snaps:
            print('WARNING: No \'externals.yaml\' created because no valid '
                  'snapshots were found. \n'
                  '  If you are trying to use a system level snapshot make '
                  'sure you have SPACK_MANAGER_EXTERNAL pointing to '
                  'spack-manager directory for the system.\n')
            return
        else:
            snap_path = os.path.join(extern_dir, snaps[0])
    else:
        snap_path = args.path

    # check that directory of ext view exists
    if not snap_path or not ev.is_env_dir(snap_path):
        tty.die('External path must point to a spack environment with a view. '
                'Auto detection of the latest dated snapshot can be achived'
                ' with the \'--latest\' flag.')

    snap_env = ev.Environment(snap_path)
    snap_env.check_views()

    if not snap_env.views:
        tty.die('Environments used to create externals must have at least 1'
                ' associated view')
    # copy the file and overwrite any that may exist (or merge?)
    inc_name_abs = os.path.abspath(os.path.join(env.path, args.name))

    try:
        detected = assemble_dict_of_detected_externals(
            snap_env, args.blacklist, args.whitelist)
        src = create_yaml_from_detected_externals(detected)
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

    env.write()


def add_command(parser, command_dict):
    ext = parser.add_parser('external',
                            help='tools for configuring precompiled'
                            ' binaries', conflict_handler='resolve')

    ext.add_argument('-n',
                     '--name', required=False,
                     help='name the new include file for the '
                     'externals with this name')
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
                     help='print a list of the available externals to use.')
    ext.set_defaults(merge=False,
                     name='externals.yaml', latest=False, list=False)

    command_dict['external'] = external
