from manager_cmds.find_machine import *
from unittest.mock import patch
import pytest


@pytest.mark.parametrize("test_function", [is_cee, is_snl_hpc, is_jlse])
def test_functional_checks_dont_return_false_positives(test_function):
    assert test_function('abcdefghijklmnopqrstuvwxyz') == False
    assert test_function('ABCDEFGHIJKLMNOPQRSTUVWXYZ') == False
    assert test_function('0123456789') == False
