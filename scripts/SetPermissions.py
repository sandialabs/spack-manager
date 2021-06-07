"""
Module to set permissions uniformly
"""

import shutil

def recursive_func(path, func, arg):
    for dirpath, dirnames, filenames in os.walk(path):
        func(dirpath, arg)
        for filename in filenames:
            func(os.path.join(dirpath, filename), arg)

def recursive_chown(path, owner):
    recursive_func(path, func=shutil.chown, arg=owner)

def recursive_chgrp(path, group):
    recursive_func(path, func=shutil.chgrp, arg=group)

def recursive_chmod(path, spec):
    recursive_func(path, func=shutil.chmod, arg=spec)

def set_dir_permissions(location, permissions, group):
    recursive_chmod(location, permissions)
    recursive_chgrp(location, group)
