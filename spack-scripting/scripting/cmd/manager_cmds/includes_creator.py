import os

import ruamel.yaml as yaml

import spack.config
import spack.util.spack_yaml as syaml


class IncludesCreator():
    def __init__(self):
        self.config = spack.config.Configuration()

    def add_scope(self, name, path):
        scope = spack.config.ConfigScope(name, os.path.abspath(path))
        self.config.push_scope(scope)

    def write_includes(self, path):
        abspath = os.path.abspath(path)
        sections = list(spack.config.section_schemas.keys())
        data = syaml.syaml_dict()
        try:
            for s in sections:
                data[s] = self.config.get_config(s)
        except (yaml.YAMLError, IOError):
            raise spack.config.ConfigError("Error reading configuration: %s" % s)

        with open(abspath, 'w') as fout:
            syaml.dump_config(data,
                              stream=fout, default_flow_style=False, blame=False)
