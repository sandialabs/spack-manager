from spack import *
from spack.pkg.builtin.trilinos import Trilinos as bTrilinos

class Trilinos(bTrilinos, CudaPackage):
    # cuda stuff from PR #17900
    conflicts('+cuda', when='~tpetra')
    depends_on('kokkos-nvcc-wrapper', when='+cuda')
    depends_on('ninja', type='build')
    generator = 'Ninja'

    def setup_environment(self, spack_env, run_env):
        if '+cuda' in self.spec:
            spack_env.set('NVCC_WRAPPER_DEFAULT_COMPILER', spack_cxx)
            spack_env.set('OMPI_CXX', join_path(self.stage.path, 'Trilinos', 'packages', 'kokkos', 'bin', 'nvcc_wrapper'))
            spack_env.set('CUDACXX', join_path(self.spec['cuda'].prefix, 'bin', 'nvcc'))


    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define

        cxx_flags = []

        def define_tpl_enable(cmake_var, spec_var=None):
             if spec_var is None:
                spec_var = cmake_var.lower()
             return self.define_from_variant('TPL_ENABLE_' + cmake_var,
                                            spec_var)

        options = super(Trilinos, self).cmake_args()
        options.append(define_tpl_enable('CUDA'))
        options.append(define('Trilinos_ENABLE_TESTS',(
            True if self.run_tests else False)))

        if '+cuda' in spec:
            cxx_flags.append(
                '--expt-extended-lambda'
            )
            options.extend([
                define('Kokkos_ENABLE_Cuda_Lambda', True),
                define('Kokkos_ENABLE_Cuda_UVM', True),
            ])

        if len(cxx_flags):
            for item in options:
                if 'CMAKE_CXX_FLAGS' in item:
                    ind = options.index(item)
                    options[ind] += " " + " ".join(cxx_flags)

        return options
