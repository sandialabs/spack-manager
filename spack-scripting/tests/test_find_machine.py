from tabnanny import verbose
from manager_cmds.find_machine import *
from unittest.mock import patch


@patch('manager_cmds.find_machine.socket.gethostname',
       return_value='abcdefghijklmnopqrstuvwxyz1234567890'
       'ABCDEFGHILJKLMNOPQRSTUVWXYZ')
def test_find_machine_doesnt_return_arbitrary_true(mock_socket):
    assert find_machine(verbose=False) == 'NOT-FOUND'
