#!/usr/bin/env spack-python
"""
This script will cycle over all packages installed
in an environment and update git source code
repos for packages with specific names.
"""
import spack.environment as ev
from spack.environment import installed_specs
import spack.util.executable
import os
import sys

git = spack.util.executable.which('git')


def GetValidEnvironment(env):
    try:
        return ev.read(env)
    except:
        try:
            ev.Environment(env)
        except:
            raise ev.SpackEnvironmentErrror(
                '%s is not a valid environment' % env)
        finally:
            return ev.Environment(env)
    return None


def UpdateDevelopmentSpecs(e):
    package_names = ['trilinos']
    env = GetValidEnvironment(e)
    with env:
        for spec in installed_specs():
            if spec.package.name in package_names:
                path = spec.package.stage.source_path
                version = str(spec.package.version)
                origin = 'origin/' + version
                print('Resetting git repo to %s in stage: %s' % (origin, path), flush=True)
                os.chdir(path)
                git('fetch', '--all')
                git('reset', '--hard', origin)
                git('clean', '-df')
                git('submodule', 'update')
                git('status', '-uno')


def Parse(args):
    parser = argparse.ArgumentParser(
        description='Cycle spec stages and update them')
    parser.add_argument(
        '-e', '--environment', required=False,
        help='Single environment with spec stages to update')
    return parser.parse_args()


if __name__ == "__main__":
    import argparse

    args = Parse(sys.argv[1:])

    if args.environment is not None:
        env = args.environment
        UpdateDevelopmentSpecs(env)
