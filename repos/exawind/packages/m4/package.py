from spack import *
from spack.pkg.builtin.m4 import M4 as bM4
import os

class M4(bM4):
    depends_on('texinfo', type='build')
