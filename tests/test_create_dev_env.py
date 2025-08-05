# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import spack.environment as ev
import manager.manager_cmds.create_dev_env as create_dev_env
import spack.main

manager = spack.main.SpackCommand("manager")


def test_allSpecsCallSpackDevelop(tmpdir, on_moonlight, monkeypatch, arg_capture):
    with tmpdir.as_cwd():
        monkeypatch.setattr(create_dev_env, "develop", arg_capture)
        manager("create-dev-env", "-s", "amr-wind@main", "nalu-wind@master", "exawind@master")
        assert arg_capture.num_calls == 3

        arg_capture.assert_call_matches(0, ["amr-wind@main"])
        arg_capture.assert_call_matches(1, ["nalu-wind@master"])
        arg_capture.assert_call_matches(2, ["exawind@master"])


def test_newEnvironmentIsCreated(tmpdir, on_moonlight, monkeypatch, arg_capture_patch):
    assert hasattr(create_dev_env, "develop")
    with tmpdir.as_cwd():

        def dev_patch(*args):
            arg_list = list(args)
            spec = arg_list[-1]
            name = spec.split("@")[0]
            os.mkdir(name)

        mock = arg_capture_patch(dev_patch)
        monkeypatch.setattr(create_dev_env, "develop", mock)
        manager("create-dev-env", "-s", "amr-wind@main", "nalu-wind@master", "exawind@master")
        assert os.path.isfile(tmpdir.join("spack.yaml"))
        assert os.path.isfile(tmpdir.join("include.yaml"))
        assert os.path.isdir(tmpdir.join("amr-wind"))
        assert os.path.isdir(tmpdir.join("nalu-wind"))
        assert os.path.isdir(tmpdir.join("exawind"))


def test_newEnvironmentKeepingUserSpecifiedYAML(tmpdir, on_moonlight, monkeypatch, arg_capture):
    with tmpdir.as_cwd():
        monkeypatch.setattr(create_dev_env, "develop", arg_capture)
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
        print(e.manifest.yaml_content)
        print(list(e.user_specs))
        assert os.path.isfile(str(tmpdir.join("spack.yaml")))
        assert os.path.isfile(str(tmpdir.join("include.yaml")))
        assert "path" in e.manifest.yaml_content["spack"]["develop"]["amr-wind"]
        assert "path" in e.manifest.yaml_content["spack"]["develop"]["nalu-wind"]
        # mocked out call that would update yaml with trilinos info but
        # assuming it works fine
        arg_capture.assert_any_call(["--path", amr_path.strpath, "amr-wind@main"])
        arg_capture.assert_any_call(["--path", nalu_path.strpath, "nalu-wind@master"])
        arg_capture.assert_any_call(["trilinos@master"])


def test_nonConcreteSpecsDontGetCloned(tmpdir, monkeypatch, arg_capture):
    with tmpdir.as_cwd():
        monkeypatch.setattr(create_dev_env, "develop", arg_capture)
        manager(
            "create-dev-env", "-s", "amr-wind", "nalu-wind", "exawind@master", "-d", tmpdir.strpath
        )
        arg_capture.assert_call_matches(-1, ["exawind@master"])
        e = ev.Environment(tmpdir.strpath)
        assert "nalu-wind" in e.manifest.yaml_content["spack"]["specs"]
        assert "exawind@master" in e.manifest.yaml_content["spack"]["specs"]
        assert "amr-wind" in e.manifest.yaml_content["spack"]["specs"]


def test_noSpecsIsNotAnErrorGivesBlankEnv(tmpdir, monkeypatch, arg_capture):
    with tmpdir.as_cwd():
        monkeypatch.setattr(create_dev_env, "develop", arg_capture)
        manager("create-dev-env", "-d", tmpdir.strpath)
        assert arg_capture.num_calls == 0
        e = ev.Environment(tmpdir.strpath)
        assert len(e.user_specs) == 0
        assert e.manifest.yaml_content["spack"]["specs"] == []
