import spack.cmd
import spack.cmd.common.arguments as arguments


def external(parser, args):
    env = spack.cmd.require_active_env(cmd_name='external')
    # check that directory of view exists
    # search for externals.yaml in the directory
    # copy the file and overwrite any that may exist (or merge?)
    # search for `external.yaml` in the spack:includes and add if it is missing



def add_command(parser, command_dict):
    external_prsr = parser.add_parser('external', help='tools for configuring precompiled'
                                  ' binaries', conflict_handler='resolve')
    external_prsr.add_argument('-d', '--dependencies', required=False, help='set all the dependencies of this package as externals')
    arguments.add_common_arguments(external_prsr, ['spec'])
    external_prsr.add_argument('path', help='The location of the external install directory')
    command_dict['external'] = external
