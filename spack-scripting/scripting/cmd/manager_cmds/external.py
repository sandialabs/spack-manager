import os

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


def create_external_yaml_from_env(path, black_list, white_list, view_key):
    env = ev.Environment(path)

    # TODO add some error checking for if no views are present
    view = env.views[view_key]

    specs = env._get_environment_specs()
    roots = env.roots()
    data = "packages:\n"

    for s in view.specs_for_view(specs, roots):
        if black_list:
            if s.name in black_list:
                continue
            else:
                data += write_spec(view, s)
        elif white_list:
            if s.name in white_list:
                data += write_spec(view, s)
        else:
            data += write_spec(view, s)
    return syaml.load_config(data)


def external(parser, args):
    env = ev.active_environment()
    if not env:
        tty.die('spack manager external requires an active environment')
    # check that directory of ext view exists
    if not ev.is_env_dir(args.path):
        tty.die('path must point to a spack environment')

    # copy the file and overwrite any that may exist (or merge?)
    if args.name:
        inc_name = args.name
    else:
        inc_name = 'externals.yaml'

    inc_name_abs = os.path.abspath(os.path.join(env.path, inc_name))
    src = create_external_yaml_from_env(
        args.path, args.blacklist, args.whitelist, args.view)

    if include_entry_exists(env, inc_name):
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
        add_include_entry(env, inc_name)
        final = src

    with open(inc_name_abs, 'w') as fout:
        syaml.dump_config(final, stream=fout,
                          default_flow_style=False)


def add_command(parser, command_dict):
    ext = parser.add_parser('external',
                            help='tools for configuring precompiled'
                            ' binaries', conflict_handler='resolve')

    ext.add_argument('-d',
                     '--dependencies', required=False,
                     help='set all the dependencies of this package '
                     'as externals')
    ext.add_argument('-n',
                     '--name', required=False,
                     help='name the new include file for the '
                     'externals with this name')
    ext.add_argument('-v', '--view', required=False, default='default',
                     help='name of view to use in the environment')
    ext.add_argument('--merge', required=False, dest='merge',
                     action='store_true', help='merge existing yaml files together')

    select = ext.add_mutually_exclusive_group()

    select.add_argument('-w',
                        '--whitelist', nargs='*', required=False,
                        help='(not implemeted) specs that should '
                        'be added (omit all others)')

    select.add_argument('-b',
                        '--blacklist', nargs='*', required=False,
                        help='(not implemented) specs that should '
                        'be omitted (add all others)')

    ext.add_argument('path',
                     help='The location of the external install '
                     'directory')
    ext.set_defaults(merge=False)

    command_dict['external'] = external
