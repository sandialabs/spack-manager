from spack import *
from spack.pkg.builtin.openfast import Openfast as bOpenfast

class Openfast(bOpenfast):
    """inherit from  builtin to fix issues and customize"""
    version('master', branch='main')
