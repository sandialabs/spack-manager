import os
import shutil

import llnl.util.tty as tty

import spack.config
import spack.environment as ev
import spack.util.spack_yaml as syaml
from spack.environment import config_dict


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


def external(parser, args):
    if args.blacklist or args.whitelist:
        tty.die('Blake and white lists have not been implemented yet')
    env = ev.active_environment()
    if not env:
        tty.die('spack manager external requires an active environment')
    # check that directory of ext view exists
    view_path = os.path.join(args.path, 'external.yaml')
    if os.path.isfile(view_path):
        # copy the file and overwrite any that may exist (or merge?)
        if args.name:
            inc_name = args.name
        else:
            inc_name = 'external.yaml'

        inc_name_abs = os.path.abspath(os.path.join(env.path, inc_name))
        view_path_abs = os.path.abspath(view_path)

        if include_entry_exists(env, inc_name):
            assert os.path.isfile(inc_name_abs)
            assert os.path.isfile(view_path_abs)

            # merge the existing includes with the new one
            # giving precedent to the new data coming in
            src = spack.config.read_config_file(
                view_path_abs, spack.config.section_schemas['packages'])
            dest = spack.config.read_config_file(
                inc_name_abs, spack.config.section_schemas['packages'])
            combined = spack.config.merge_yaml(src, dest)

            with open(inc_name_abs, 'w') as fout:
                syaml.dump_config(combined, stream=fout,
                                  default_flow_style=False)
        else:
            add_include_entry(env, inc_name)
            shutil.copy2(view_path_abs, inc_name_abs)

    else:
        raise tty.die('No external.yaml file has been written'
                      ' to the specified directory')


def add_command(parser, command_dict):
    external_prsr = parser.add_parser('external',
                                      help='tools for configuring precompiled'
                                      ' binaries', conflict_handler='resolve')

    external_prsr.add_argument('-d',
                               '--dependencies', required=False,
                               help='set all the dependencies of this package '
                               'as externals')
    external_prsr.add_argument('-n',
                               '--name', required=False,
                               help='name the new include file for the '
                               'externals with this name')

    select_group = external_prsr.add_mutually_exclusive_group()

    select_group.add_argument('-w',
                              '--whitelist', nargs='*', required=False,
                              help='(not implemeted) specs that should '
                              'be added (omit all others)')

    select_group.add_argument('-b',
                              '--blacklist', nargs='*', required=False,
                              help='(not implemented) specs that should '
                              'be omitted (add all others)')

    external_prsr.add_argument('path',
                               help='The location of the external install '
                               'directory')

    command_dict['external'] = external
