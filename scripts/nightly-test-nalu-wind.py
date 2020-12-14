#!/usr/bin/env spack-python
from spack.main import SpackCommand
import pathlib
import sys
import os

install = SpackCommand('install')
env = SpackCommand('env')

env('activate', '{envName}'.format(envName=sys.argv[1]))
install('--overwrite','-y','nalu-wind-nightly')
env('view','regenerate')
