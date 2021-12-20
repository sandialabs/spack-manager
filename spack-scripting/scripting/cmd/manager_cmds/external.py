import spack.cmd
import spack.cmd.common.arguments as arguments

extern_template = r"""  {name}:
                          externals:
                          - spec: {spec}
                            prefix: {prefix}
                          buildable: False"""

def external(parser, args):
    env = spack.cmd.require_active_env(cmd_name='external')
    for view_desc in env.views.values():
        with open('external_defs.yaml', 'w') as ext_log:
            ext_log.write('packages:')

            specs = view_desc.specs_for_view()
            for spec in specs:



def add_command(parser, command_dict):
    external_prsr = parser.add_parser('external', help='tools for configureing precompiled'
                                  ' binaries', conflict_handler='resolve')
    external_prsr.add_argument('-d', '--dependencies', required=False, help='set all the dependencies of this package as externals')
    arguments.add_common_arguments(external_prsr, ['spec'])
    external_prsr.add_argument('path', help='The location of the external install directory')
    command_dict['external'] = external