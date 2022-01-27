from spack import *
from spack.pkg.builtin.trilinos import Trilinos as bTrilinos
import os

class Trilinos(bTrilinos):
    variant('stk_unit_tests', default=False,
            description='turn on STK unit tests')

    patch('kokkos.patch', when='+cuda')

    def setup_dependent_package(self, module, dependent_spec):
        if '+wrapper' in self.spec:
            # Hardcode nvcc_wrapper path to avoid kokkos-nvcc-wrapper error with trilinos as an external
            self.spec.kokkos_cxx = os.path.join(os.getenv('SPACK_MANAGER'), 'bin', 'nvcc_wrapper')
        else:
            self.spec.kokkos_cxx = spack_cxx

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(Trilinos, self).cmake_args()

        options.append(self.define_from_variant('STK_ENABLE_TESTS', 'stk_unit_tests'))

        return options
