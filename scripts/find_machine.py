#!/usr/bin/env spack-python

import sys
import os
import socket

def is_cee(hostname):
    known_hosts = ('cee', 'ews', 'ecs', 'hpws')
    for k in known_hosts:
        if k in hostname:
            return True
    return False

def find_machine():
    hostname = socket.gethostname()
    if sys.platform == 'darwin':
        machine = 'darwin'
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        # NREL machines
        if 'NREL_CLUSTER' in os.environ:
            if os.environ['NREL_CLUSTER'] == 'eagle':
                machine = 'eagle'
            # Set this in your .bashrc on rhodes
            elif os.environ['NREL_CLUSTER'] == 'rhodes':
                machine = 'rhodes'
        # SNL machines
        else:
            if 'skybridge' in hostname:
                machine = 'skybridge'
            elif 'ascicgpu' in hostname:
                machine = 'ascicgpu'
            elif is_cee(hostname):
                machine = 'cee'
            elif 'ghost' in hostname:
                machine = 'ghost'
    else:
        machine = 'NOT-FOUND'

    return machine

if __name__ == '__main__':
    print(find_machine())

