#!/usr/bin/env spack-python

import argparse
import os
import sys

import spack.environment as ev

template = r"""  {name}:
    externals:
    - spec: {short_spec}
      prefix: {prefix}
    buildable: false
"""

def write_spec(ext_file, view, spec):
    ext_file.write(template.format(
        name = spec.name,
        short_spec = spec.short_spec,
        prefix = view.root
    ))


def create_external_yaml(args):
    env = ev.Environment(args.env)

    if args.view:
        view = env.views[args.view]
    else:
        view = env.views['default']

    fext = os.path.join(view.root, 'externals.yaml')
    with open(fext, 'w') as f:
        specs = env._get_environment_specs()
        roots = env.roots()
        for s in view.specs_for_view(specs, roots):
            if not s.external:
                write_spec(f, view, s)


def parse(data):
    parser = argparse.ArgumentParser(
        description='Create a list of externals from installed environment with view')
    parser.add_argument(
        'env', help='environment to create the extenals with')
    parser.add_argument(
        '--view', '-v', required=False, help='view to create externals for')
    return parser.parse_args(data)


if __name__ == '__main__':
    args = parse(sys.argv[1:])
    create_external_yaml(args)
