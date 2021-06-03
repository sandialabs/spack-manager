#!/usr/bin/env spack-python
"""
A script to create  view files
"""
from spack.main import SpackCommand
import spack.environment as ev
import sys
import os

def CreateView(my_env, view_name):
    view = SpackCommand('view')
    loc = SpackCommand('location')
    env = SpackCommand('env')
    new_view = os.path.join(os.environ['SPACK_MANAGER'],'view',view_name)

    if not ev.exists(my_env):
        raise Exception('Env not installed')

    with ev.read(my_env):
        # get list of spec names
        spec_list = ev.read(my_env).roots()
        for spec in spec_list:
            print(spec)
            view('copy', new_view, spec)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create a view in the spack-manager')
    parser.add_argument('-e','--env_name',required=True,help='Name/path to environment for view creation',)
    parser.add_argument('-v','--view_name',required=True,help='Name of the view',)
    args = parser.parse_args()
    CreateView(args.env_name,args.view_name)
