from tempfile import TemporaryDirectory
import pytest

import spack.main

manager = spack.main.SpackCommand('manager')


def test_mustHaveActiveEnvironment(tmpdir):
    with tmpdir.as_cwd():
        with pytest.raises(spack.main.SpackCommandError):
            manager('external', 'add', 'nalu-wind', '/usr')

