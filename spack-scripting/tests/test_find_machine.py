import pytest
from manager_cmds.find_machine import *


@pytest.mark.parametrize("test_function", [is_cee, is_snl_hpc, is_jlse])
def test_functional_checks_dont_return_false_positives(test_function):
    assert test_function('abcdefghijklmnopqrstuvwxyz') is False
    assert test_function('ABCDEFGHIJKLMNOPQRSTUVWXYZ') is False
    assert test_function('0123456789') is False
