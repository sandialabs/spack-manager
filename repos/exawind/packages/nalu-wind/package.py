from spack import *
from spack.pkg.builtin.nalu_wind import NaluWind as bNaluWind
from spack.pkg.builtin.kokkos import Kokkos
import os
from shutil import copyfile

class NaluWind(bNaluWind, CudaPackage):
    depends_on('kokkos-nvcc-wrapper', when='+cuda')
    depends_on('boost cxxstd=11')
    #generator = 'Ninja'
    #depends_on('ninja-fortran', type='build')
    depends_on('trilinos+cuda', when='+cuda')
    for val in CudaPackage.cuda_arch_values:
        arch_string='cuda_arch={arch}'.format(arch=val)
        depends_on('trilinos+wrapper+cuda_rdc {arch}'.format(arch=arch_string), when=arch_string)
    variant('wind_utils',default=False,
            description='Build wind-utils')
    variant('set_tmpdir', default='default',
            description='Change tmpdir env variabte in build')
    variant('asan', default=False,
            description='turn on address sanitizer')
    variant('compile_commands', default=False,
            description='generate compile_commands.json and copy to source dir')

    def setup_build_environment(self, env):
        spec = self.spec
        if spec.variants['set_tmpdir'].value != 'default':
            env.set('TMPDIR', spec.variants['set_tempdir'].value)

        if '+cuda' in spec:
            if '+mpi' in spec:
                env.set('OMPI_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            else:
                env.set('CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
        else:
            env.set(
                "KOKKOS_ARCH_" +
                Kokkos.spack_micro_arch_map[spec.target.name].upper(), True)

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(NaluWind, self).cmake_args()

        cxx_flags =''

        if '+compile_commands' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if '+wind_utils' in spec:
            options.append(define('ENABLE_WIND_UTILS', True))
        else:
            options.append(define('ENABLE_WIND_UTILS', False))

        if  '+cuda' in spec:
            options.append(define('ENABLE_CUDA', True))

        if '+asan' in spec:
            cxx_flags+=' -fsanitize=address -fno-sanitize-address-use-after-scope'

        options.append(define('CMAKE_CXX_FLAGS',cxx_flags))
        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        if '+compile_commands' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
