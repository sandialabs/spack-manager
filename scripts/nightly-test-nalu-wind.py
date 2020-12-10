#!/usr/bin/env spack-python
from spack.main import SpackCommand
import sys
import os

install = SpackCommand('install')
env = SpackCommand('env')
uninstall = SpackCommand('uninstall')

env('activate', '{envName}'.format(envName=sys.argv[1]))
uninstall('-y','nalu-wind-nightly', fail_on_error=False)
install('-v','nalu-wind-nightly')

#view = SpackCommand('view')
# create view replacing previous nightly
