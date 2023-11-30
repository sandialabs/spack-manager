import os
import socket
import sys


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
