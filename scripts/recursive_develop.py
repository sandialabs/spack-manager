#! /usr/bin/env spack-python
import argparse
import spack.cmd

import spack.main

develop = spack.main.SpackCommand("develop")
#def develop(spec):
#    print(f"Calling spack develop on {spec}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('spec', help='Spec to recursively call spack develop until the root is hit.', default=None)
    return parser.parse_args()

def develop_dependents(input, env):
    specs = spack.cmd.parse_specs(input)
    if len(specs) > 1:
        raise SpackError("spack develop requires at most one named spec")
    spec = specs[0]

    print(f"Calling spack develop {input}")
    develop(input)

    concrete_specs = env.all_matching_specs(spec)
    if not concrete_specs:
        return
    for cspec in concrete_specs:
        parents = cspec.dependents()
        for p in parents:
            develop_dependents(p.format("{name}@{version}"), env)
    return


def main():
    args = parse_args()
    env = spack.cmd.require_active_env(cmd_name="recursive")
    with env:
        develop_dependents(args.spec, env)

            
if __name__ == "__main__":
    main()
