import os

import llnl.util.tty as tty

from manager_cmds.includes_creator import IncludesCreator

import spack.cmd
import spack.cmd.common.arguments as arguments
import spack.environment as ev


def external(parser, args):
    env = ev.active_environment()
    if not env:
        tty.die('spack manager external requires and active environment')
    # check that directory of ext view exists
    fpath = os.path.join(args.path, 'external.yaml')
    if os.path.isfile(fpath):
        pass
    else:
        raise tty.die('No external.yaml file has been written'
                      ' to the specified directory')
    # search for externals.yaml in the directory
    # copy the file and overwrite any that may exist (or merge?)
    # search for `external.yaml` in the spack:includes and add if it is missing



def add_command(parser, command_dict):
    external_prsr = parser.add_parser('external', help='tools for configuring precompiled'
                                  ' binaries', conflict_handler='resolve')
    external_prsr.add_argument('-d', '--dependencies', required=False, help='set all the dependencies of this package as externals')
    external_prsr.add_argument('path', help='The location of the external install directory')
    command_dict['external'] = external
