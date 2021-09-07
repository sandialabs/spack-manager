from spack.pkg.builtin.trilinos import Trilinos as bTrilinos
import os

class Trilinos(bTrilinos):
    if os.environ['SPACK_MANAGER_MACHINE'] != 'summit':
        depends_on('ninja', type='build')
        generator = 'Ninja'

    # Last known working GPU commit
    # version('develop', commit='4796b92fb0644ba8c531dd9953e7a4878b05c62d')
