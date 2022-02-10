#!/usr/bin/env spack-python
import manager_cmds.find_machine as find_machine


def get_path_to_externals():
    machine = find_machine.find_machine(verbose=False)
    if machine in ['cee', 'snl-hpc', 'ascicgpu']:
        return '/projects/wind/spack-manager'
    elif machine in ['eagle']:
        return '/projects/exawind/exawind-snapshots/spack-manager'
    else:
        return


if __name__ == '__main__':
    path = get_path_to_externals()
    # echo path if it exists
    if path:
        print(path)
