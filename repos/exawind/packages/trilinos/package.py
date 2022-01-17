from spack import *
from spack.pkg.builtin.trilinos import Trilinos as bTrilinos

class Trilinos(bTrilinos, ROCmPackage):
    variant('stk_unit_tests', default=False,
            description='turn on STK unit tests')

    patch('kokkos.patch', when='+cuda')

    amdgpu_arch_map = {
        'gfx900': 'vega900',
        'gfx906': 'vega906',
        'gfx908': 'vega908',
        'gfx90a': 'vega90A'
    }
    amd_support_conflict_msg = (
        '{0} is not supported; '
        'Kokkos supports the following AMD GPU targets: '
        + ', '.join(amdgpu_arch_map.keys()))
    for arch in ROCmPackage.amdgpu_targets:
        if arch not in amdgpu_arch_map:
            conflicts('+rocm', when='amdgpu_target={0}'.format(arch),
                      msg=amd_support_conflict_msg.format(arch))

    def setup_build_environment(self, env):
        spec = self.spec
        if spec.satisfies('+cuda') and spec.satisfies('+wrapper'):
            if '+mpi' in spec:
                env.set('OMPI_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
                env.set('MPICH_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
                env.set('MPICXX_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            else:
                env.set('CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)

        if spec.satisfies('+rocm'):
            if '+stk' in spec:
                # Using CXXFLAGS for hipcc which isn't in the spack wrappers
                env.set('CXXFLAGS', '-DSTK_NO_BOOST_STACKTRACE')
            if '+mpi' in spec:
                env.set('OMPI_CXX', self.spec['hip'].hipcc)
                env.set('MPICH_CXX', self.spec['hip'].hipcc)
                env.set('MPICXX_CXX', self.spec['hip'].hipcc)
            else:
                env.set('CXX', self.spec['hip'].hipcc)

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(Trilinos, self).cmake_args()

        amd_microarches = []
        if "+rocm" in spec:
            options.append(define('Kokkos_ENABLE_ROCM', False))
            options.append(define('Kokkos_ENABLE_HIP', True))
            if '+tpetra' in spec:
                options.append(define('Tpetra_INST_HIP', True))
            for amdgpu_target in spec.variants['amdgpu_target'].value:
                if amdgpu_target != "none":
                    if amdgpu_target in self.amdgpu_arch_map:
                        amd_microarches.append(
                            self.amdgpu_arch_map[amdgpu_target])
            for arch in amd_microarches:
                options.append(self.define("Kokkos_ARCH_" + arch.upper(), True))

        options.append(self.define_from_variant('STK_ENABLE_TESTS', 'stk_unit_tests'))

        return options
