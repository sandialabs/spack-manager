# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os
from datetime import date

import spack.main

arch = spack.main.SpackCommand("arch")

def base_extension(use_machine_name):
    if use_machine_name:
        return "exawind/snapshots/{machine}".format(machine=os.environ["SPACK_MANAGER_MACHINE"])
    else:
        return "exawind/snapshots/{arch}".format(arch=arch("-b").strip())


def path_extension(name, use_machine_name):
    return os.path.join(
        base_extension(use_machine_name),
        "{date}".format(date=name if name else date.today().strftime("%Y-%m-%d")),
    )


def pruned_spec_string(spec, variants_to_omit=["dev_path=", "patches="]):
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
