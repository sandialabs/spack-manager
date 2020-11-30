#!/usr/bin/env spack-python
import sys
import os

from spack.spec import Spec
import spack.config


class SpackConfigRunner:
    """
    Runs script supplied with the given config either via command line
    or through the environment variable SPACK_CONFIG
    """
    def __init__(self):
        config_path=None

        if '-c' in sys.argv:
            index = sys.argv.index('-c')
            config_path = sys.argv[index+1]
        else:
            config_path = os.environ['SPACK_CONFIG']

        if os.path.exists(config_path):
            self.my_scope=spack.config.ConfigScope('local', config_path)
        else:
            raise Exception('Specified scope doesn\'t exist',config_path)

    def __call__(self, func, *args, **kargs):
        """call function with the desired scope"""
        with spack.config.override(self.my_scope):
            func(*args, **kargs)
