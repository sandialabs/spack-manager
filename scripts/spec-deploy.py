#!/usr/bin/env spack-python
from spack.main import SpackCommand
import pathlib
import sys
import os

install = SpackCommand('install')
env = SpackCommand('env')

env_name = sys.argv[1]
spec_name = " ".join(sys.argv[2:])

if env_name not in env('ls'):
    print('Environment {env} has not been created'.format(env=env_name))
    exit(10)


env('activate', '{envName}'.format(envName=env_name))
install('--overwrite','-y','{spec}'.format(spec=spec_name))
env('view','enable')
env('view', 'loads', '-r')
env('deactivate', '{envName}'.format(envName=env_name))
