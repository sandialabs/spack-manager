# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import spack.util.spack_yaml as syaml
from spack.extensions.manager.environment_utils import SpackManagerEnvironmentManifest as smem


def test_smManifestCanSetConfig(tmpdir):
    with tmpdir.as_cwd():
        with open("spack.yaml", "w") as f:
            f.write("spack:\n specs: []")

        testManifest = smem(tmpdir.strpath)
        assert list(testManifest.version_compatible_config_generator())
        testManifest.set_config_value("config", "install_tree", {"root": "$env/opt"})
        assert "config" in testManifest.yaml_content["spack"]
        testManifest.append_includes("include.yaml")
        testManifest.prepend_includes("first_include.yaml")
        testManifest.flush()

        with open("spack.yaml", "r") as f:
            yaml = syaml.load(f)
            assert "$env/opt" in yaml["spack"]["config"]["install_tree"]["root"]
            assert "include.yaml" in yaml["spack"]["include"]
            assert "first_include.yaml" == yaml["spack"]["include"][0]
