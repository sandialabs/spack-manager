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


"""
setup a dictionary with a key for machine name and checker function
for value. the checker function should return true for the machine
match
"""
machine_list = {
    'cee' : lambda : is_cee(socket.gethostname()),
    'eagle' : lambda : os.environ['NREL_CLUSTER'] == 'eagle',
    'rhodes' : lambda : os.environ['NREL_CLUSTER'] == 'rhodes',
    'summit' : lambda : os.environ['LMOD_SYSTEM_NAME'] == 'summit',
    'spock' : lambda : os.environ['LMOD_SYSTEM_NAME'] == 'spock',
    'skybridge' : lambda : 'skybridge' in socket.gethostname(),
    'ascicgpu' : lambda : 'ascicgpu' in socket.gethostname(),
    'darwin' : lambda : sys.platform == 'darwin',
}


def find_machine():
    for machine, i_am_this_machine in machine_list.items():
        """
        Since we don't expect uniform environments on all machines
        we bury our checks in a try/except
        """
        try:
            if i_am_this_machine():
                return machine
        except(KeyError):
            """
            expect key errors when an environment variable is not defined
            so these are skipped
            """
            pass
        except:
            """
            all other errors will be raised and kill the program
            we can add more excpetions to the pass list as needed
            in the future
            """
            raise
    return 'NOT-FOUND'


if __name__ == '__main__':
    print(find_machine())
