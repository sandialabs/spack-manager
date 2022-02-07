#!/usr/bin/env spack-python
from tempfile import TemporaryDirectory
import manager_cmds.find_machine as find_machine
from manager_cmds.find_machine import machine_list
import spack.environment as env
import spack.main
import argparse

manager = spack.main.SpackCommand('manager')


def check_config_concretizations(name, ref_yaml):
    print('Concretization test for', name)
    with TemporaryDirectory() as tmpdir:
        try:
            manager('create-env', '-y', ref_yaml, '-d', tmpdir, '-m', name)
            with env.Environment(tmpdir) as this_env:
                this_env.concretize()
        except Exception as err:
            raise Exception(name + ' failed to concretize.'
                            ' Additional exception: ' + str(err))

        print(name, 'concretized succesfully')


def run_tests(args):
    failure = False
    machine_names = list(machine_list.keys())
    matrix_test_machines = ['eagle', 'summit']
    this_machine = find_machine(verbose=False)

    if '_matrix.yaml' in args.yaml:
        machine_names = matrix_test_machines
    else:
        machine_names = list(set(machine_names) - set(matrix_test_machines))
    # remove from ascicgpu from darwin due to gcc conflict
    # need to test if we can move to boost@1.77
    if this_machine == 'darwin' and 'ascicgpu' in machine_names:
        machine_names.remove('ascicgpu')

    for name in machine_names:
        try:
            check_config_concretizations(name, args.yaml)
        except(Exception) as e:
            print(e)
            failure = True
            continue
    exit(failure)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Arguments for testing concretization')
    parser.add_argument('-y', '--yaml', required=True,
                        help='reference yaml for the environment')
    args = parser.parse_args()
    run_tests(args)
