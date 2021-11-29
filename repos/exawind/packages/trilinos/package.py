from spack.pkg.builtin.trilinos import Trilinos as bTrilinos
import os

class Trilinos(bTrilinos):
    patch('c++17.patch', when='cxxstd=17')
    if os.environ['SPACK_MANAGER_MACHINE'] != 'summit':
        depends_on('ninja', type='build')
        generator = 'Ninja'
