# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

# for more details.

import os

import ruamel.yaml as yaml

import spack.config
import spack.util.spack_yaml as syaml


class IncludesCreator():
    def __init__(self):
        self.config = spack.config.Configuration()

    def add_scope(self, name, path):
        """
        scopes should be added in order from lowest to highest precident
        """
        scope = spack.config.ConfigScope(name, os.path.abspath(path))
        self.config.push_scope(scope)

    def write_includes(self, path):
        abspath = os.path.abspath(path)
        sections = list(spack.config.section_schemas.keys())
        data = syaml.syaml_dict()
        try:
            for s in sections:
                # we have to check that there is data in each scope
                # or else ill-formatted output can occur
                has_data = False
                for scope in self.config.scopes.values():
                    if scope.get_section(s) is not None:
                        has_data = True
                if (has_data):
                    temp = self.config.get_config(s)
                    data[s] = temp
        except (yaml.YAMLError, IOError):
            raise spack.config.ConfigError("Error reading configuration: %s" % s)

        with open(abspath, 'w') as fout:
            syaml.dump_config(data,
                              stream=fout, default_flow_style=False, blame=False)
