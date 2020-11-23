from spack import *
from spack.pkg.builtin.nalu_wind import NaluWind as bNaluWind
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
        depends_on('trilinos+wrapper {arch}'.format(arch=arch_string), when=arch_string)
    variant('wind_utils',default=False,
            description='Build wind-utils')

    def setup_build_environment(self, env):
        spec = self.spec
        if '+cuda' in spec:
            env.set('TMPDIR', '/scratch/psakiev/tmp')
            if '+mpi' in spec:
                env.set('OMPI_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            else:
                env.set('CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(NaluWind, self).cmake_args()

        options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if '+wind_utils' in spec:
            options.append(define('ENABLE_WIND_UTILS', True))
        else:
            options.append(define('ENABLE_WIND_UTILS', False))

        if  '+cuda' in spec:
            options.append(define('ENABLE_CUDA', True))

        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        target = os.path.join(self.stage.source_path, "compile_commands.json")
        source = os.path.join(self.build_directory, "compile_commands.json")
        copyfile(source, target)
