# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os
import spack.extensions.manager.manager_cmds.create_dev_env as create_dev_env

import spack.environment as ev
import spack.main

manager = spack.main.SpackCommand("manager")


def test_allSpecsCallSpackDevelop(tmpdir, on_moonlight, monkeypatch, argtest):
    with tmpdir.as_cwd():
        monkeypatch.setattr(create_dev_env, "develop", argtest)
        manager("create-dev-env", "-s", "amr-wind@main", "nalu-wind@master", "exawind@master")
        assert argtest.num_calls == 3
        assert ["amr-wind@main"] == argtest.args[0]
        assert ["-rb", "git@github.com:Exawind/nalu-wind.git", "master", "nalu-wind@master"] == argtest.args[1]
        assert ["exawind@master"] == argtest.args[2]


def test_newEnvironmentIsCreated(tmpdir, on_moonlight, monkeypatch, argtest):
    assert hasattr(create_dev_env, "develop")
    with tmpdir.as_cwd():
        monkeypatch.setattr(create_dev_env, "develop", argtest)
        manager("create-dev-env", "-s", "amr-wind@main", "nalu-wind@master", "exawind@master")
        assert os.path.isfile(tmpdir.join("spack.yaml"))
        assert os.path.isfile(tmpdir.join("include.yaml"))


'''
@patch("spack.extensions.manager.manager_cmds.create_dev_env.develop")
def test_newEnvironmentKeepingUserSpecifiedYAML(mock_dev, tmpdir):
    with tmpdir.as_cwd():
        amr_path = tmpdir.join("test_amr-wind")
        nalu_path = tmpdir.join("test_nalu-wind")
        os.makedirs(amr_path.strpath)
        os.makedirs(nalu_path.strpath)
        assert os.path.isdir(amr_path.strpath)
        assert os.path.isdir(nalu_path.strpath)
        user_spec_yaml = """spack:
  develop:
     amr-wind:
       spec: amr-wind@main
       path: {amr}
     nalu-wind:
       spec: nalu-wind@master
       path: {nalu}""".format(
            amr=amr_path.strpath, nalu=nalu_path.strpath
        )
        with open(tmpdir.join("user.yaml"), "w") as yaml:
            yaml.write(user_spec_yaml)

        print(
            manager(
                "create-dev-env",
                "-d",
                tmpdir.strpath,
                "-s",
                "amr-wind@main",
                "nalu-wind@master",
                "trilinos@master",
                "-y",
                str(tmpdir.join("user.yaml")),
                fail_on_error=False,
            )
        )
        e = ev.Environment(tmpdir.strpath)
        print(e.manifest.pristine_yaml_content)
        print(list(e.user_specs))
        assert os.path.isfile(str(tmpdir.join("spack.yaml")))
        assert os.path.isfile(str(tmpdir.join("include.yaml")))
        assert "path" in e.manifest.pristine_yaml_content["spack"]["develop"]["amr-wind"]
        assert "path" in e.manifest.pristine_yaml_content["spack"]["develop"]["nalu-wind"]
        # mocked out call that would update yaml with trilinos info but
        # assuming it works fine
        mock_dev.assert_any_call(["--path", amr_path.strpath, "amr-wind@main"])
        mock_dev.assert_any_call(["--path", nalu_path.strpath, "nalu-wind@master"])
        mock_dev.assert_called_with(
            ["-rb", "git@github.com:trilinos/trilinos.git", "master", "trilinos@master"]
        )


@patch("spack.extensions.manager.manager_cmds.create_dev_env.develop")
def test_nonConcreteSpecsDontGetCloned(mock_dev, tmpdir):
    with tmpdir.as_cwd():
        manager(
            "create-dev-env", "-s", "amr-wind", "nalu-wind", "exawind@master", "-d", tmpdir.strpath
        )
        mock_dev.assert_called_once_with(["exawind@master"])
        e = ev.Environment(tmpdir.strpath)
        assert "nalu-wind" in e.manifest.pristine_yaml_content["spack"]["specs"]
        assert "exawind@master" in e.manifest.pristine_yaml_content["spack"]["specs"]
        assert "amr-wind" in e.manifest.pristine_yaml_content["spack"]["specs"]


@patch("spack.extensions.manager.manager_cmds.create_dev_env.develop")
def test_noSpecsIsNotAnErrorGivesBlankEnv(mock_develop, tmpdir):
    with tmpdir.as_cwd():
        manager("create-dev-env", "-d", tmpdir.strpath)
        assert not mock_develop.called
        e = ev.Environment(tmpdir.strpath)
        assert len(e.user_specs) == 0
        assert e.manifest.pristine_yaml_content["spack"]["specs"] == []
'''
