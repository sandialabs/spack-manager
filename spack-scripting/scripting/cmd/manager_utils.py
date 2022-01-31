from datetime import date
import os

import spack.main

arch = spack.main.SpackCommand('arch')


def base_extension(use_machine_name):
    if use_machine_name:
        return "exawind/snapshots/{machine}".format(
            machine=os.environ['SPACK_MANAGER_MACHINE'])
    else:
        return "exawind/snapshots/{arch}".format(
            arch=arch('-b').strip())


def path_extension(name, use_machine_name):
    return os.path.join(base_extension(use_machine_name), "{date}".format(
        date=name if name else date.today().strftime("%Y-%m-%d")))
