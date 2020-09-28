from spack import *
from spack.pkg.builtin.nalu_wind import NaluWind as bNaluWind
import os
from shutil import copyfile

class NaluWind(bNaluWind, CudaPackage):
    depends_on('kokkos-nvcc-wrapper', when='+cuda')
    depends_on('boost cxxstd=11')
    generator = 'Ninja'
    depends_on('ninja', type='build')

    def cmake_args(self):
        if self.spec.variants['test_tol']:
            self.run_tests = True
        define = CMakePackage.define
        options = super(NaluWind, self).cmake_args()
        options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))
        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        target = os.path.join(self.stage.source_path, "compile_commands.json")
        source = os.path.join(self.build_directory, "compile_commands.json")
        copyfile(source, target)
