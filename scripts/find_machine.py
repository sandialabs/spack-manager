#!/usr/bin/env spack-python

import sys
import os
import socket

if sys.platform == 'darwin':
    machine = 'darwin'
elif sys.platform == 'linux':
    # NREL machines
    if 'NREL_CLUSTER' in os.environ:
        if os.environ['NREL_CLUSTER'] == 'eagle':
            machine = 'eagle'
        elif os.environ['NREL_CLUSTER'] == 'rhodes':
            machine = 'rhodes'
    # SNL machines
    else:
        hostname = socket.gethostname()
        if 'skybridge' in hostname:
            machine = 'skybridge'
        elif 'ascicgpu' in hostname:
            machine = 'ascicgpu'
else:
    machine = 'NOT-FOUND'

print(machine)
