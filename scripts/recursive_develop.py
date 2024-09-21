#! /usr/bin/env spack-python
import argparse
import spack.cmd

import spack.main

develop = spack.main.SpackCommand("develop")
#def develop(*args):
#    print(f"Calling spack develop on {args}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('spec', help='Spec to recursively call spack develop until the root is hit.', default=None)
    parser.add_argument("--forward", "-f", help="string containing arguments to forward to 'spack develop' calls")
    return parser.parse_args()

def develop_dependents(input, env, develop_args=[]):
    specs = spack.cmd.parse_specs(input)
    if len(specs) > 1:
        raise SpackError("spack develop requires at most one named spec")
    spec = specs[0]

    calling_args=develop_args+[input]

    print(f"Calling spack develop {' '.join(calling_args)}")

    develop(*develop_args)

    concrete_specs = env.all_matching_specs(spec)
    if not concrete_specs:
        return
    for cspec in concrete_specs:
        parents = cspec.dependents()
        for p in parents:
            develop_dependents(p.format("{name}@{version}"), env, develop_args)
    return


def main():
    args = parse_args()
    env = spack.cmd.require_active_env(cmd_name="recursive")
    if args.forward:
        develop_args = args.forward.split()
    else:
        develop_args = []
    with env:
        develop_dependents(args.spec, env, develop_args)

            
if __name__ == "__main__":
    main()
