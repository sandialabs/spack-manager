# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import llnl.util.lang

import spack.util.spack_yaml as syaml
from spack.util.path import canonicalize_path

DETECTION_SCRIPT = "find-{n}.py"
DETECTION_MODULE = "find_{n}"


class Project:
    """
    This class is the in memory representation of how a software project is
    organized in spack-manager.

    At its base a Project is a collection of a spack repo and specialized configs.
    This is the basic unit that spack-manager is designed to organize.

    This class is designed to be an easy way to access the filesystem without needing a
    a bunch of os.path.join's.

    Due to the need to be synced with the filesystem it will not be something
    you want to access inside a performant loop
    """

    def __init__(self, path, config_path=None, repo_path=None):
        self.root = canonicalize_path(path)
        self.name = os.path.basename(self.root)
        if config_path:
            self.config_path = canonicalize_path(config_path)
        else:
            self.config_path = os.path.join(self.root, "configs")

        if repo_path:
            self.repo_path = canonicalize_path(repo_path)
        else:
            self.repo_path = os.path.join(self.root, "repo")

        # default is to detect nothing.
        self.detector = lambda _: False
        # machine upstream root for creating externals
        self.upstream_root = lambda _: False

        # create missing directories
        os.makedirs(self.config_path, exist_ok=True)
        os.makedirs(self.repo_path, exist_ok=True)
        self._populate_machines()
        self._machine_detector()

    def _machine_detector(self):
        detection_script = os.path.join(self.root, DETECTION_SCRIPT.format(n=self.name))
        assert os.path.isfile(detection_script)
        if os.path.isfile(detection_script):
            # dynamically import the find script for the project here
            # so we can just load the detection script
            mod = llnl.util.lang.load_module_from_file(
                DETECTION_MODULE.format(n=self.name), detection_script
            )
            assert mod
            self.detector = mod.detector

    def _populate_machines(self):
        self.machines = []
        machine_dirs = list(os.scandir(self.config_path))
        for machine in machine_dirs:
            self.machines.append(machine.name)


_default_config = """
spack-manager:
    projects: {}
"""
_default_config_path = os.path.realpath(
    os.path.abspath(os.path.join(__file__, "..", "..", "spack-manager.yaml"))
)

config_path = _default_config_path
config_yaml = {}
projects = {}


def populate_config():
    """Update the spack-manager config in memory"""
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


def __init__():
    populate_config()
    load_projects()
