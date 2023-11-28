# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import spack.environment.environment as senv


class SpackManagerEnvironmentManifest(senv.EnvironmentManifestFile):
    """Spack-Manager extensiont to the manifest file for prototyping"""

    def set_config_value(self, root, key, value):
        """Set/overwrite a config value

        Args:
            root: config root (i.e. config, packages, etc)
            key: next level where we will be updating
            value: value to set
        """
        self.pristine_yaml_content.get(root, {})[key] = value
        self.yaml_content.get(root, {})[key] = value
        self.changed = True

    def append_includes(self, value):
        """Add to the includes in the manifest

        Args:
            value: value to add at the end of the list
        """
        self.pristine_yaml_content.get("include", []).append(value)
        self.yaml_content.get("include", []).append(value)
        self.changed = True

    def prepend_includes(self, value):
        """Add to the includes in the manifest

        Args:
            value: value to add at the beginning of the list
        """
        self.pristine_yaml_content.get("include", [])[:0] = [value]
        self.yaml_content.get("include", [])[:0] = [value]
        self.changed = True
