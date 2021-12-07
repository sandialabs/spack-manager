import os
import socket
import sys


def is_cee(hostname):
    known_hosts = ('cee', 'ews', 'ecs', 'hpws')
    for k in known_hosts:
        if k in hostname:
            return True
    return False


def is_snl_hpc(hostname):
    known_hosts = ('skybridge', 'ghost', 'attaway', 'chama')
    for k in known_hosts:
        if k in hostname:
            return True
    return False


"""
Set up a dictionary with a key for machine name and checker function
for value - the checker function should return true for the machine
match
"""
machine_list = {
    # SNL
    'cee': lambda: is_cee(socket.gethostname()),
    'snl-hpc': lambda: is_snl_hpc(socket.gethostname()),
    'ascicgpu': lambda: 'ascicgpu' in socket.gethostname(),
    # NREL
    'eagle': lambda: os.environ['NREL_CLUSTER'] == 'eagle',
    'rhodes': lambda: os.environ['NREL_CLUSTER'] == 'rhodes',
    'darwin': lambda: sys.platform == 'darwin',
    # OLCF
    'summit': lambda: os.environ['LMOD_SYSTEM_NAME'] == 'summit',
    'spock': lambda: os.environ['LMOD_SYSTEM_NAME'] == 'spock',
}


"""
Set up a dictionary with a key for fully qualified domain
name and machine name
"""
machine_with_domain_list = {
    # SNL
    'cee': 'cee.hpc.snl.gov',
    'snl-hpc': 'snl-hpc.hpc.snl.gov',
    'ascicgpu': 'ascicgpu.hpc.snl.gov',
    # NREL
    'eagle': 'eagle.hpc.nrel.gov',
    'rhodes': 'rhodes.hpc.nrel.gov',
    'darwin': 'darwin.hpc.nrel.gov',
    # OLCF
    'summit': 'summit.olcf.ornl.gov',
    'spock': 'spock.olcf.ornl.gov',
}


def find_machine(parser=None, args=None, verbose=True):
    for machine, i_am_this_machine in machine_list.items():
        """
        Since we don't expect uniform environments on all machines
        we bury our checks in a try/except
        """
        try:
            if i_am_this_machine():
                if verbose:
                    print(machine)
                return machine
        except(KeyError):
            """
            expect key errors when an environment variable is not defined
            so these are skipped
            """
            pass
        except(Exception):
            """
            all other errors will be raised and kill the program
            we can add more excpetions to the pass list as needed
            in the future
            """
            raise
    if verbose:
        print('NOT-FOUND')
    return 'NOT-FOUND'


def add_command(parser, command_dict):
    parser.add_parser('find-machine',
                      help='get the current machine detected by spack-manager')
    command_dict['find-machine'] = find_machine
