from spack import *
from spack.pkg.builtin.nalu_wind import NaluWind as bNaluWind

class NaluWind(bNaluWind, CudaPackage):
    depends_on('kokkos-nvcc-wrapper', when='+cuda')
    depends_on('boost cxxstd=11')

    def cmake_args(self):
        define = CMakePackage.define
        options = super(NaluWind, self).cmake_args()
        options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))
        return options
