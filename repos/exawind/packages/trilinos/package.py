from spack import *
from spack.pkg.builtin.trilinos import Trilinos as bTrilinos

class Trilinos(bTrilinos):
    variant('stk_unit_tests', default=False,
            description='turn on STK unit tests')

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(Trilinos, self).cmake_args()

        options.append(self.define_from_variant('STK_ENABLE_TESTS', 'stk_unit_tests'))

        return options
