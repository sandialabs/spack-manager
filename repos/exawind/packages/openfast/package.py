from spack import *
from spack.pkg.exawind.openfast import Openfast as bOpenfast

class Openfast(bOpenfast):
    """inherit from  builtin to fix issues and customize"""
    versions('master', branch='main')
