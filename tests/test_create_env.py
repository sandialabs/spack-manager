# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import pytest

import spack.environment as env
import spack.extensions.manager.manager_cmds.create_env as create_env
import spack.main
import spack.util.spack_yaml as syaml

manager = spack.main.SpackCommand("manager")
envcmd = spack.main.SpackCommand("env")


def test_basicDirectoryProperties(tmpdir, on_moonlight):
    with tmpdir.as_cwd():
        manager("create-env", "-d", tmpdir.strpath, "-m", "moonlight", "-s", "binutils")
        assert os.path.isfile("spack.yaml")
        assert os.path.isfile("include.yaml")

        with open("spack.yaml", "r") as f:
            yaml = syaml.load(f)
            assert "concretizer" in yaml["spack"]
            assert yaml["spack"]["concretizer"]["unify"] is True


def test_failsWithAnUnregisteredMachine(tmpdir):
    with tmpdir.as_cwd():
        with pytest.raises(Exception):
            manager("create-env", "-d", tmpdir, "-m", "theGOAT_HPC")


def test_specsCanBeAddedToExisitingYaml(tmpdir, on_moonlight):
    with tmpdir.as_cwd():
        preset_yaml = """
spack:
  develop:
    amr-wind:
      spec: amr-wind@main
      path: /tst/dir"""

        with open("test.yaml", "w") as fyaml:
            fyaml.write(preset_yaml)

        env_root = str(tmpdir.join("dev"))
        os.makedirs(env_root)

        assert os.path.isfile("test.yaml")
        manager(
            "create-env",
            "-d",
            env_root,
            "-m",
            "moonlight",
            "-y",
            "test.yaml",
            "-s",
            "amr-wind",
            "nalu-wind",
        )

        e = env.Environment(env_root)
        assert e.manifest.pristine_yaml_content["spack"]["specs"][0] == "amr-wind"
        assert e.manifest.pristine_yaml_content["spack"]["specs"][1] == "nalu-wind"
        assert (
            e.manifest.pristine_yaml_content["spack"]["develop"]["amr-wind"]["spec"]
            == "amr-wind@main"
        )
        assert (
            e.manifest.pristine_yaml_content["spack"]["develop"]["amr-wind"]["path"] == "/tst/dir"
        )
        assert "view" not in e.manifest.pristine_yaml_content["spack"].keys()


def test_existingYamlViewIsNotOverwritten(tmpdir, on_moonlight):
    with tmpdir.as_cwd():
        preset_yaml = """
spack:
  view: true
  develop:
    amr-wind:
      spec: amr-wind@main
      path: /tst/dir"""

        with open("test.yaml", "w") as fyaml:
            fyaml.write(preset_yaml)

        env_root = str(tmpdir.join("dev"))
        os.makedirs(env_root)

        assert os.path.isfile("test.yaml")

        manager("create-env", "-d", env_root, "-y", "test.yaml", "-s", "amr-wind", "nalu-wind")

        e = env.Environment(env_root)
        assert e.manifest.pristine_yaml_content["spack"]["view"]


def test_specs_can_have_spaces(tmpdir, on_moonlight):
    with tmpdir.as_cwd():
        manager("create-env", "-s", "nalu-wind ", " build_type=Release", "%gcc")


def test_unify_in_yaml_preserved(tmpdir, on_moonlight):
    with tmpdir.as_cwd():
        preset_yaml = """
spack:
    specs: [amr-wind, nalu-wind]
    concretizer:
        unify: when_possible"""

        with open("template.yaml", "w") as f:
            f.write(preset_yaml)

        manager("create-env", "-y", "template.yaml")
        e = env.Environment(tmpdir.strpath)
        assert "when_possible" == e.manifest.pristine_yaml_content["spack"]["concretizer"]["unify"]


def test_local_source_tree_can_be_added_to_env(tmpdir, on_moonlight):
    with tmpdir.as_cwd():
        manager("create-env", "-s", "nalu-wind", "-l")
        e = env.Environment(tmpdir.strpath)
        assert (
            "$env/opt"
            in e.manifest.pristine_yaml_content["spack"]["config"]["install_tree"]["root"]
        )
