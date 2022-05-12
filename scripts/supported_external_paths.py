#!/usr/bin/env spack-python
#
#Copyright (c) 2022, National Technology & Engineering Solutions of Sandia, LLC
#(NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
#Government retains certain rights in this software.
#
#This software is released under the BSD 3-clause license. See LICENSE file
#for more details.
#
import manager_cmds.find_machine as find_machine


def get_path_to_externals():
    machine = find_machine.find_machine(verbose=False)
    if machine in ['cee', 'snl-hpc', 'ascicgpu', 'ascic']:
        return '/projects/wind/spack-manager'
    elif machine in ['eagle']:
        return '/projects/exawind/exawind-snapshots/spack-manager'
    elif machine in ['rhodes']:
        return '/projects/ecp/exawind/exawind-snapshots/spack-manager'
    elif machine in ['summit']:
        # This is currently on a project scratch directory and is
        # unfortunately subject to purge
        return '/gpfs/alpine/proj-shared/cfd116/jrood/spack-manager-summit'
    else:
        return


if __name__ == '__main__':
    path = get_path_to_externals()
    # echo path if it exists
    if path:
        print(path)
