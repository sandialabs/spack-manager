# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os
from datetime import date

import spack.main
from spack.extensions.manager.manager_cmds.find_machine import find_machine

arch = spack.main.SpackCommand("arch")


def base_extension(use_machine_name):
    if use_machine_name:
        machine = find_machine()
        return "snapshots/exawind/{0}".format(machine)
    else:
        return "snapshots/exawind/{arch}".format(arch=arch("-b").strip())


def path_extension(name, use_machine_name):
    return os.path.join(
        base_extension(use_machine_name),
        "{date}".format(date=name if name else date.today().strftime("%Y-%m-%d")),
    )


def pruned_spec_string(spec, variants_to_omit=["dev_path=", "patches=", "build_system="]):
    full_spec = spec.format("{name}{@version}{%compiler}{variants}{arch=architecture}")
    spec_components = full_spec.split(" ")

    def filter_func(entry):
        for v in variants_to_omit:
            if v in entry:
                return False
        return True

    pruned_components = list(filter(filter_func, spec_components))

    pruned_spec = " ".join(pruned_components)
    return pruned_spec


def command(command, *args):
    """
    Execute a spack.main.SpackCommand uniformly
    and add some print statements
    """
    print("spack", command.command_name, *args)
    print(command(*args, fail_on_error=False))
