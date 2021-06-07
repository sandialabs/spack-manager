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
          raise ev.SpackEnvironmentErrror('%s is not a valid environment' % env)
       finally:
          return ev.Environment(env)
    return None


def GetListOfEnvironments(iFile):
    envs = []
    with open(iFile) as fp:
        name, frequency = fp.readline().split()
        envs.append({'name' : name,'freq' : frequency})
    return envs

def TimeToUpdate(f):
    """
    Check if the environment should be built
    based off the specified frequency and current
    date
    """
    today = date.today()

    if f == 'monthly' and today.day == 1:
        return True
    if f == 'daily':
        return True
    if f == 'quarterly' and today.day == 1 and today.month in [1,4,7,10]:
        return True

    return False

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
            git('pull')
            git('submodule', 'update')

def UpdateEnvironment(e):
    env = GetValidEnvironment(e)
    with env:
        env.install_all()


def UpdateListOfEnvironments(inputFile):
    envs = GetListOfEnvironments(inputFile)
    for e in envs:
        if TimeToUpdate(e['freq']):
            UpdateEnvironment(e['name'])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description = 'Cycle environments and update them')
    parser.add_argument('-i', '--input_file', required = False, help = 'File with list of envrionments to update')
    parser.add_argument('-e', '--environment', required = False, help = 'Single environment to update without checking frequency')
    parser.add_argument('-u', '--update_spack_manager', action='store_true', help = 'Update spack-manager before updating environments')
    parser.set_defaults(update_spack_manager=False)
    args = parser.parse_args()

    if args.update_spack_manager:
        os.chdir(os.environ['SPACK_MANAGER'])
        git('pull')
        git('submodule', 'update')

    if args.input_file is not None:
        UpdateListOfEnvironments(args.input_file)

    if args.environment is not None:
        env = args.environment
        UpdateDevelopmentSpecs(env)
        UpdateEnvironment(env)

