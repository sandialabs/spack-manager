import os
import pytest

import spack.environment as ev
import spack.main

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


def test_firstTimeAddingExternal(tmpdir):
    yaml_file = r"""spack:
  view: true
  specs: [mpileaks]"""
    with tmpdir.as_cwd():
        manifest = tmpdir.join('spack.yaml')

        with open(str(manifest), 'w') as f:
            f.write(yaml_file)

        env('create', '-d', '.', 'spack.yaml', )

        with ev.Environment('.') as e:
            assert os.path.isdir(e.view_path_default)
            extfile = os.path.join(e.view_path_default, 'external.yaml')
            with open(extfile, 'w') as ff:
                ff.write('packages:')
            manager('external',  e.view_path_default)
            includes = config_dict(e.yaml).get('include', [])
            assert 1 == len(includes)
            assert 'external.yaml' == str(includes[0])
            
