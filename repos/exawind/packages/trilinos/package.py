from spack.pkg.builtin.trilinos import Trilinos as bTrilinos

class Trilinos(bTrilinos):
    depends_on('ninja', type='build')
    generator = 'Ninja'
