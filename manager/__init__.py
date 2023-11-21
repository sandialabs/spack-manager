# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os
import spack.util.spack_yaml as syaml
# from project import Project
from spack.util.path import canonicalize_path

DETECTION_SCRIPT_NAME = "dectector.py"

class Project:
    """
    This class is the in memory representation of how a software project is
    organized in spack-manager.
    It is designed to be an easy way to access the filesystem without needing a
    a bunch of os.path.join's.
    Due to the need to be synced with the filesystem it will not be something
    you want to access inside a performant loop
    """
    def __init__(self, path):
        self.root = canonicalize_path(path)
        self.config_path = os.path.join(self.root, "configs")
        self.repo_path = os.path.join(self.root, "repo")
        # create missing directories
        os.makedirs(self.config_path, exist_ok=True)
        os.makedirs(self.repo_path, exist_ok=True)
        self.populate_machines()
        self.machine_detector()


    def machine_detector(self):
        self.detector = lambda _ : False
        detection_script = os.path.join(self.root, "find-machine.py")
        if os.path.isfile(detection_script):
            locals = {}
            exec(detection_script, globals(), locals)
            self.detector = locals["detector"]


    def populate_machines(self):
        self.machines = []
        machine_path = os.path.join(self.root, "configs")
        machine_dirs = list(os.scandir(os.path.join(self.root, "configs")))
        for machine in machine_dirs:
            self.machines.append(machine.name)


_default_config = """
spack-manager:
    projects: {}
"""
config_path = os.path.realpath(
    os.path.abspath(os.path.join(__file__, "..", "..", "spack-manager.yaml"))
)

config_yaml = {}
projects = {}

def populate_config():
    """ Update the spack-manager config in memory"""
    global config_yaml
    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            config_yaml = syaml.load(f)
    else:
        config_yaml = syaml.load(_default_config)

def load_projects():
    global projects
    projects_node = config_yaml["spack-manager"]["projects"]
    for key, path in projects_node.items():
        projects[key] = Project(path)

# module init stuff
populate_config()
load_projects()

