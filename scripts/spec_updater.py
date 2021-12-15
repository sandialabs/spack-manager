#!/usr/bin/env spack-python
"""
This script will cycle over a list of environments
and update them.  These environments should control
the views that modules use.
"""
import spack.environment as ev
import spack.util.executable
from datetime import date
import os
import sys

git = spack.util.executable.which('git')


def GetValidEnvironment(env):
    try:
        # check for registerd env
        return ev.read(env)
    except:
        try:
            # check for anonymous env
            ev.Environment(env)
        except:
            raise ev.SpackEnvironmentErrror(
                '%s is not a valid environment' % env)
        finally:
            return ev.Environment(env)
    return None


def UpdateDevelopmentSpecs(e):
    env = GetValidEnvironment(e)
    with env:
        for name, entry in env.dev_specs.items():
            os.chdir(os.path.join(env.path, entry['path']))
            print('Updating develop spec for: %s' % name)
            try:
                git('fetch', '--unshallow', error=os.devnull)
            except:
                pass
            git('fetch', '--all')
            git('reset', '--hard', 'HEAD')
            git('clean', '-df')
            git('submodule', 'update')
            git('status', '-uno')


def Parse(args):
    parser = argparse.ArgumentParser(
        description='Cycle specs and update them')
    parser.add_argument(
        '-e', '--environment', required=False,
        help='Single environment with specs to update')
    return parser.parse_args()


if __name__ == "__main__":
    import argparse

    args = Parse(sys.argv[1:])

    if args.environment is not None:
        env = args.environment
        UpdateDevelopmentSpecs(env)
