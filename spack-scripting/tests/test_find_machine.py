# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import pytest
from manager_cmds.find_machine import is_cee, is_jlse, is_tlcc2


@pytest.mark.parametrize("test_function", [is_cee, is_tlcc2, is_jlse])
def test_functional_checks_dont_return_false_positives(test_function):
    assert test_function("abcdefghijklmnopqrstuvwxyz") is False
    assert test_function("ABCDEFGHIJKLMNOPQRSTUVWXYZ") is False
    assert test_function("0123456789") is False
