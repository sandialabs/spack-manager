# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os


class MachineData:
    def __init__(self, test, full_machine_name=None):
        self.i_am_this_machine = test
        self.full_machine_name = full_machine_name


def detector(name):
    machine_list = {"moonlight": MachineData(lambda: "MOONLIGHT" in os.environ)}
    if name in machine_list:
        return machine_list[name].i_am_this_machine()
    else:
        return False

class Detector:
    def __init__(self):
        self.machine_list = {"moonlight": MachineData(lambda: "MOONLIGHT" in os.environ)}

    def __call__(self, name):
        if name in machine_list:
            return machine_list[name].i_am_this_machine()
        else:
            return False
