from spack import *
from spack.pkg.builtin.trilinos import Trilinos as bTrilinos
import os

class Trilinos(bTrilinos):
    depends_on('ninja', type='build')
    generator = 'Ninja'
