# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from environment_utils import SpackManagerEnvironmentManifest as smem

import spack.util.spack_yaml as syaml


def test_smManifestCanSetConfig(tmpdir):
    with tmpdir.as_cwd():
        with open("spack.yaml", "w") as f:
            f.write("spack:\n specs: []")

        testManifest = smem(tmpdir.strpath)
        testManifest.set_config_value("config", "install_tree", {"root": "$env/opt"})
        testManifest.append_includes("include.yaml")
        testManifest.flush()

        with open("spack.yaml", "r") as f:
            yaml = syaml.load(f)
            assert "$env/opt" in yaml["spack"]["config"]["install_tree"]["root"]
            assert "include.yaml" in yaml["spack"]["include"]
