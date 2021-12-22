import os

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
            manager('external', 'add', '/path/to/view')


def test_errorsIfThereIsNoExternalYaml(tmpdir):
    yaml_file = r"""spack:
  view: true
  specs: [mpileaks]"""
    with tmpdir.as_cwd():
        path = tmpdir.join('spack.yaml')
        with open(str(path), 'w') as f:
            f.write(yaml_file)
        env('create', '-d', '.', 'spack.yaml', )
        env('activate', '-d', '.')
        e = ev.Environment('.')
        assert os.path.isdir(e.view_path_default)
        with pytest.raises(spack.main.SpackCommandError):
            manager('external',  e.view_path_default)


class ExtPackage:
    def __init__(self, name, spec, prefix):
        self.name = name
        self.spec = spec
        self.prefix = prefix
        self.package_str = r"""  {name}:
    externals:
    - spec: {spec}
      prefix: {prefix}
    buildable: False
""".format(name=name, spec=spec, prefix=prefix)

    def __str__(self):
        return self.package_str


ext_cmake = ExtPackage('cmake', 'cmake@3.21.0', '/path/to/view')
generic_external_yaml = 'packages:\n' + str(ext_cmake)


def evaluate_external(tmpdir, yaml_file):
    manifest = tmpdir.join('spack.yaml')

    with open(str(manifest), 'w') as f:
        f.write(yaml_file)

    env('create', '-d', '.', 'spack.yaml', )

    with ev.Environment('.') as e:
        assert os.path.isdir(e.view_path_default)
        extfile = os.path.join(e.view_path_default, 'external.yaml')
        with open(extfile, 'w') as ff:
            ff.write(generic_external_yaml)
        manager('external',  e.view_path_default)
        includes = config_dict(e.yaml).get('include', [])
        assert 1 == len(includes)
        assert 'external.yaml' == str(includes[0])


def test_firstTimeAddingExternal(tmpdir):
    with tmpdir.as_cwd():
        yaml_file = r"""spack:
  view: true
  specs: [mpileaks]"""
        evaluate_external(tmpdir, yaml_file)
        with open('external.yaml', 'r') as f:
            yaml = syaml.load(f)
            assert yaml['packages']['cmake']


def test_addToExistingExternal(tmpdir):
    with tmpdir.as_cwd():
        yaml_file = r"""spack:
  view: true
  include:
    - external.yaml
  specs: [mpileaks]
    """
        old_manifest = str(tmpdir.join('external.yaml'))
        with open(old_manifest, 'w') as f:
            f.write('packages:\n')
            f.write(str(ExtPackage('openmpi', 'openmpi@4.0.3', '/path/to/other/view')))

        evaluate_external(tmpdir, yaml_file)

        with open('external.yaml', 'r') as f:
            yaml = syaml.load(f)
            assert yaml['packages']['openmpi']
            assert yaml['packages']['cmake']
