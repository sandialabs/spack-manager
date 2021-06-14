#! /usr/bin/env python3
"""
Module to set permissions uniformly
"""

import shutil
import os
import stat

def recursive_file_system_func(path, func, kargs):
    for dirpath, dirnames, filenames in os.walk(path):
        kargs['path'] = dirpath
        func(**kargs)
        for filename in filenames:
            kargs['path'] = os.path.join(dirpath, filename)
            func( **kargs)

def recursive_chown(path, user=None, group=None):
    kargs = {
        'user' : user,
        'group' : group
    }
    recursive_file_system_func(path, shutil.chown, kargs)

def recursive_chgrp(path, group):
    recursive_chown(path, None, group)

def recursive_chmod(path, spec):
    kargs = {
        'mode' : spec
    }
    recursive_file_system_func(path, os.chmod, kargs)

def set_dir_permissions(location, permissions, group):
    recursive_chmod(location, permissions)
    recursive_chgrp(location, group)

if __name__ == '__main__':
    import sys
    set_dir_permissions(sys.argv[1],0o755,'wg-sierra-users')
