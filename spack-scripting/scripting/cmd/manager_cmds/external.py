import os
import shutil

import llnl.util.tty as tty

from manager_cmds.includes_creator import IncludesCreator

import spack.cmd
import spack.cmd.common.arguments as arguments
import spack.environment as ev
from spack.environment import config_dict


def include_exists(env, name):
    includes = config_dict(env.yaml).get('include', [])
    for entry in includes:
        if entry == name:
            return True
    return False


def add_include_entry(env, inc, prepend=True):
    includes = config_dict(env.yaml).get('include', [])
    if prepend:
        includes.insert(0, inc)
    else:
        includes.append(inc)
    env.write()


def external(parser, args):
    if args.blacklist or args.whitelist:
        tty.die('Blake and white lists have not been implemented yet')
    env = ev.active_environment()
    if not env:
        tty.die('spack manager external requires an active environment')
    # check that directory of ext view exists
    fpath = os.path.join(args.path, 'external.yaml')
    if os.path.isfile(fpath):
        # copy the file and overwrite any that may exist (or merge?)
        if args.name:
            ext_name = args.name
        else:
            ext_name = 'external.yaml'

        if include_exists(env, ext_name):
            # merge the existing includes with the new one
            # giving precedent to the new data coming in
            merger = IncludesCreator()
            merger.add_scope('old', ext_name)
            merger.add_scope('new', fpath)
            merger.write_includes(ext_name)
        else:
            add_include_entry(env, ext_name)
            shutil.copy2(fpath, ext_name)

    else:
        raise tty.die('No external.yaml file has been written'
                      ' to the specified directory')


def add_command(parser, command_dict):
    external_prsr = parser.add_parser('external', help='tools for configuring precompiled'
                                  ' binaries', conflict_handler='resolve')
    external_prsr.add_argument('-d', '--dependencies', required=False, help='set all the dependencies of this package as externals')
    external_prsr.add_argument('-n', '--name', required=False, help='name the new include file for the externals with this name')
    # todo mutualy exclusive group for blacklist an whitelists
    select_group = external_prsr.add_mutually_exclusive_group()
    select_group.add_argument('-w', '--whitelist', nargs='*', required=False, help='specs that should be added (omit all others)')
    select_group.add_argument('-b', '--blacklist', nargs='*', required=False, help='specs that should be omitted (add all others)')
    external_prsr.add_argument('path', help='The location of the external install directory')
    command_dict['external'] = external
