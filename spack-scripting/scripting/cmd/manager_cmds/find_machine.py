import os
import socket
import sys


class MachineData:
    def __init__(self, test, full_machine_name):
        self.i_am_this_machine=test
        self.full_machine_name=full_machine_name


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
    'cee': MachineData(lambda: is_cee(socket.gethostname()), 'cee.snl.gov'),
    'snl-hpc': MachineData(lambda: is_snl_hpc(socket.gethostname()), 'snl-hpc.snl.gov'),
    'ascicgpu': MachineData(lambda: 'ascicgpu' in socket.gethostname(), 'ascicgpu.snl.gov'),
    # NREL
    'eagle': MachineData(lambda: os.environ['NREL_CLUSTER'] == 'eagle', 'eagle.hpc.nrel.gov'),
    'rhodes': MachineData(lambda: os.environ['NREL_CLUSTER'] == 'rhodes', 'rhodes.hpc.nrel.gov'),
    'darwin': MachineData(lambda: sys.platform == 'darwin', 'darwin.hpc.nrel.gov'),
    # OLCF
    'summit': MachineData(lambda: os.environ['LMOD_SYSTEM_NAME'] == 'summit', 'summit.olcf.ornl.gov'),
    'spock': MachineData(lambda: os.environ['LMOD_SYSTEM_NAME'] == 'spock', 'spock.olcf.ornl.gov'),
}


def find_machine(parser=None, args=None, verbose=True, full_machine_name=False):
    for machine_name, data in machine_list.items():
        """
        Since we don't expect uniform environments on all machines
        we bury our checks in a try/except
        """
        try:
            if data.i_am_this_machine():
                if verbose:
                    print(machine_name)
                if full_machine_name:
                    return data.full_machine_name
                else:
                    return machine_name
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
