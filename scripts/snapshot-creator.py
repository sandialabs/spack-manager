#!/usr/bin/env spack-python
"""
This script will create the snapshots we need for the exawind project
and any associated modules
"""

import argparse
import os
import sys
from manager_cmds.find_machine import find_machine

import spack.environment as ev
import spack.main

from datetime import date

arch = spack.main.SpackCommand('arch')
manager = spack.main.SpackCommand('manager')


def parse(stream):
    parser = argparse.ArgumentParser(
        'create a timestamped snapshot for a Exawind machines')
    parser.add_argument(
        '-m', '--modules', action='store_true', help="create modules to associate with each view in the environment")
    parser.set_defaults(modules=False)

    return parser.parse_args(stream)


def path_extension():
    return "exawind/snapshots/{arch}/{date}".format(
        date=date.today().strftime("%Y%m%d"),
        arch=arch('-t'))


# TODO embed this info into find_machine.py
cuda_machines = ['eagle', 'ascicgpu']


def add_specs(env, machine):

    # ensure concretization is separate
    env.yaml['spack']['concretization'] = 'separately'
    specs = env.yaml['spack']['specs']
    specs.append(
        {'matrix': [['exawind+hypre+openfast+tioga'], ['~cuda']]}
    )

    # update matrix based on machine specific architecture
    if machine in cuda_machines:
        specs[-1]['matrix'][1].append(
            '+cuda +amr_wind_gpu +nalu_wind_gpu cuda_arch=70')


def add_views(env, machine, extension):
    view = env.yaml['spack']['view']
    prefix = os.path.join(os.environ['SPACK_MANAGER'], 'views')
    # can we get away with just 1 view?
    # todo link type as a parameter ?
    view = {'base': {'root': os.path.join(prefix, extension, 'cpu'),
                     'link_type': 'hardlink'}}


def add_modules(env, machine, extension):
    pass


def create_snapshots(args):
    machine = find_machine(verbose=False)
    extension = path_extension()
    env_path = os.path.join(
        os.environ['SPACK_MANAGER'], 'environments', extension)

    manager('create-env', '-d', env_path)
    with ev.Environment(env_path) as e:
        # update the spack.yaml in memory so we down't have to carry
        # unnecessary templates for each machine
        add_specs(e, machine)
        add_views(e, machine, extension)
        if args.modules:
            add_modules(e, machine, extension)

        # e.concretize()
        # e.install_all()


if __name__ == '__main__':
    args = parse(sys.argv[1:])
    create_snapshots(args)
