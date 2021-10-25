#!/usr/bin/env spack-python
from tempfile import TemporaryDirectory
from find_machine import machine_list
import create_machine_spack_environment as cmse
import spack.environment as env


def check_config_concretizations(name):
    print('Concretization test for', name)
    with TemporaryDirectory() as tmpdir:
        args = cmse.Parse(['-d', tmpdir, '-m', name])
        cmse.CreateEnvDir(args)
        try:
            with env.Environment(tmpdir) as this_env:
                this_env.concretize()
        except:
            print(name, 'failed to concretize')
            return
        print(name, 'concretized succesfully')


if __name__ == '__main__':
    machine_names = list(machine_list.keys())
    for name in machine_names:
        check_config_concretizations(name)
