# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import manager.manager_cmds.external as m_external
import pytest
from manager.manager_cmds.external import external
from manager.manager_utils import pruned_spec_string

import spack.environment as ev
import spack.main
import spack.util.spack_yaml as syaml
from spack.spec import Spec

env = spack.main.SpackCommand("env")
manager = spack.main.SpackCommand("manager")


@pytest.mark.parametrize(
    "spec_str",
    [
        "amr-wind@main dev_path=/amr-wind",
        "nalu-wind@master+cuda cuda_arch=70 " "dev_path=/nalu-wind",
        "exawind@master dev_path=/exawind "
        "^nalu-wind@master dev_path=/nalu-wind"
        " ^amr-wind@main dev_path=/amr-wind",
    ],
)
def test_stripDevPathFromExternals(spec_str):
    assert "dev_path" in spec_str
    s = Spec(spec_str)
    pruned_string = pruned_spec_string(s)
    assert "dev_path" not in pruned_string


@pytest.mark.parametrize(
    "spec_str",
    [
        "amr-wind@main patches=abscdef",
        "nalu-wind@master+cuda cuda_arch=70 " "patches=asldfkjas",
        "exawind@master patches=fxfdcx "
        "^nalu-wind@master patches=dtafwuf"
        " ^amr-wind@main patches=windenergy",
    ],
)
def test_stripPatchesFromExternals(spec_str):
    assert "patches" in spec_str
    s = Spec(spec_str)
    pruned_string = pruned_spec_string(s)
    assert "patches" not in pruned_string


def test_mustHaveActiveEnvironment(tmpdir, on_moonlight):
    with tmpdir.as_cwd():
        with pytest.raises(spack.main.SpackCommandError):
            manager("external", "/path/to/view")


class ParserMock:
    def __init__(
        self,
        path,
        view="default",
        name="externals.yaml",
        whitelist=None,
        blacklist=None,
        merge=False,
        latest=False,
    ):
        self.path = path
        self.view = view
        self.name = name
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.merge = merge
        self.latest = False
        self.list = False


def setupExternalEnv(tmpdir, has_view=True):
    yaml_file = """spack:
  view: {v}
  specs: [cmake@3.20.0]""".format(
        v=has_view
    )
    env_path = str(tmpdir.join("external"))
    os.makedirs(env_path, exist_ok=True)
    os.makedirs(str(tmpdir.join("test")), exist_ok=True)
    with open(os.path.join(env_path, "spack.yaml"), "w") as f:
        f.write(yaml_file)
    return env_path


def test_failsWithNoProject(tmpdir):
    yaml_file = """spack:
  view: true
  specs: [mpileaks]"""
    with tmpdir.as_cwd():
        ext_env = setupExternalEnv(tmpdir, False)
        path = tmpdir.join("spack.yaml")
        with open(str(path), "w") as f:
            f.write(yaml_file)
        env("create", "-d", "test", "spack.yaml")
        args = ParserMock(ext_env)
        with pytest.raises(SystemExit):
            with ev.Environment("test"):
                external(None, args)


def test_errorsIfThereIsNoView(tmpdir, on_moonlight):
    yaml_file = """spack:
  view: true
  specs: [mpileaks]"""
    with tmpdir.as_cwd():
        ext_env = setupExternalEnv(tmpdir, False)
        path = tmpdir.join("spack.yaml")
        with open(str(path), "w") as f:
            f.write(yaml_file)
        env("create", "-d", "test", "spack.yaml")
        args = ParserMock(ext_env)
        with pytest.raises(SystemExit):
            with ev.Environment("test"):
                external(None, args)


class ExtPackage:
    def __init__(self, name, spec, prefix):
        self.name = name
        self.spec = spec
        self.prefix = prefix
        self.package_str = """  {name}:
    externals:
    - spec: {spec}
      prefix: {prefix}
    buildable: False
""".format(
            name=name, spec=spec, prefix=prefix
        )

    def __str__(self):
        return self.package_str


def evaluate_external(tmpdir, yaml_file, monkeypatch, arg_capture_patch, on_moonlight):
    ext_path = setupExternalEnv(tmpdir)
    manifest = tmpdir.join("spack.yaml")

    with open(str(manifest), "w") as f:
        f.write(yaml_file)

    env("create", "-d", "test", "spack.yaml")
    assert os.path.isfile("test/spack.yaml")

    with ev.Environment("test") as e:
        args = ParserMock(ext_path, merge=True)

        def impl_mock(*args):
            return str(ExtPackage("cmake", "cmake@3.20.0", "/path/top/some/view"))

        mock_write = arg_capture_patch(impl_mock)
        monkeypatch.setattr(m_external, "write_spec", mock_write)
        external(None, args)
        # check that the include entry was added to the spack.yaml
        assert mock_write.num_calls == 1
        includes = e.configuration.get("include", [])
        assert 1 == len(includes)
        assert "externals.yaml" == str(includes[0])


@pytest.mark.skip()
def test_firstTimeAddingExternal(tmpdir, monkeypatch, arg_capture_patch, on_moonlight):
    with tmpdir.as_cwd():
        yaml_file = """spack:
  view: true
  specs: [mpileaks]"""
        evaluate_external(tmpdir, yaml_file, monkeypatch, arg_capture_patch, on_moonlight)
        assert os.path.isfile("test/externals.yaml")
        with open("test/externals.yaml", "r") as f:
            yaml = syaml.load(f)
            print(yaml)
            assert yaml["packages"]  # ['cmake']


@pytest.mark.skip()
def test_addToExistingExternal(tmpdir, monkeypatch, arg_capture_patch, on_moonlight):
    with tmpdir.as_cwd():
        yaml_file = """spack:
  view: true
  include:
    - externals.yaml
  specs: [mpileaks]
    """
        setupExternalEnv(tmpdir)
        old_manifest = str(tmpdir.join("test/externals.yaml"))
        with open(old_manifest, "w") as f:
            f.write("packages:\n")
            f.write(str(ExtPackage("openmpi", "openmpi@4.0.3", "/path/to/other/view")))

        evaluate_external(tmpdir, yaml_file, monkeypatch, arg_capture_patch, on_moonlight)

        with open("test/externals.yaml", "r") as f:
            yaml = syaml.load(f)
            assert yaml["packages"]["openmpi"]
            assert yaml["packages"]["cmake"]
