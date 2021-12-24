import os
from unittest.mock import patch

import manager_cmds
import manager_cmds.external
import pytest

import spack.environment as ev
import spack.main
import spack.util.spack_yaml as syaml
from spack.environment import config_dict

env = spack.main.SpackCommand('env')
manager = spack.main.SpackCommand('manager')


def test_mustHaveActiveEnvironment(tmpdir):
    with tmpdir.as_cwd():
        with pytest.raises(spack.main.SpackCommandError):
            manager('external', '/path/to/view')


class ParserMock:
    def __init__(self, path,
                 view='default',
                 name='externals.yaml',
                 whitelist=None,
                 blacklist=None,
                 merge=False):
        self.path = path
        self.view = view
        self.name = name
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.merge = merge


def setupExternalEnv(tmpdir, has_view=True):
    yaml_file = """spack:
  view: {v}
  specs: [cmake@3.20.0]""".format(v=has_view)
    env_path = str(tmpdir.join('external'))
    os.makedirs(env_path, exist_ok=True)
    os.makedirs(str(tmpdir.join('test')), exist_ok=True)
    with open(os.path.join(env_path, 'spack.yaml'), 'w') as f:
        f.write(yaml_file)
    return env_path


def test_errorsIfThereIsNoView(tmpdir):
    yaml_file = """spack:
  view: true
  specs: [mpileaks]"""
    with tmpdir.as_cwd():
        ext_env = setupExternalEnv(tmpdir, False)
        path = tmpdir.join('spack.yaml')
        with open(str(path), 'w') as f:
            f.write(yaml_file)
        env('create', '-d', 'test', 'spack.yaml', )
        args = ParserMock(ext_env)
        with pytest.raises(SystemExit):
            with ev.Environment('test'):
                manager_cmds.external.external(None, args)


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
""".format(name=name, spec=spec, prefix=prefix)

    def __str__(self):
        return self.package_str


def evaluate_external(tmpdir, yaml_file):
    ext_path = setupExternalEnv(tmpdir)
    manifest = tmpdir.join('spack.yaml')

    with open(str(manifest), 'w') as f:
        f.write(yaml_file)

    env('create', '-d', 'test', 'spack.yaml', )
    assert os.path.isfile('test/spack.yaml')

    with ev.Environment('test') as e:
        args = ParserMock(ext_path, merge=True)
        with patch("manager_cmds.external.write_spec",
                   return_value=str(
                       ExtPackage(
                           'cmake', 'cmake@3.20.0', '/path/top/some/view')
                   )) as mock_write:
            manager_cmds.external.external(None, args)
        # check that the include entry was added to the spack.yaml
        assert mock_write.called_once()
        includes = config_dict(e.yaml).get('include', [])
        assert 1 == len(includes)
        assert 'externals.yaml' == str(includes[0])


@pytest.mark.skip()
def test_firstTimeAddingExternal(tmpdir):
    with tmpdir.as_cwd():
        yaml_file = """spack:
  view: true
  specs: [mpileaks]"""
        evaluate_external(tmpdir, yaml_file)
        assert os.path.isfile('test/externals.yaml')
        with open('test/externals.yaml', 'r') as f:
            yaml = syaml.load(f)
            print(yaml)
            assert yaml['packages']  # ['cmake']


@pytest.mark.skip()
def test_addToExistingExternal(tmpdir):
    with tmpdir.as_cwd():
        yaml_file = """spack:
  view: true
  include:
    - externals.yaml
  specs: [mpileaks]
    """
        setupExternalEnv(tmpdir)
        old_manifest = str(tmpdir.join('test/externals.yaml'))
        with open(old_manifest, 'w') as f:
            f.write('packages:\n')
            f.write(
                str(ExtPackage('openmpi', 'openmpi@4.0.3', '/path/to/other/view')))

        evaluate_external(tmpdir, yaml_file)

        with open('test/externals.yaml', 'r') as f:
            yaml = syaml.load(f)
            assert yaml['packages']['openmpi']
            assert yaml['packages']['cmake']
