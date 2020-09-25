from spack import *
from spack.pkg.builtin.nalu_wind import NaluWind as bNaluWind

class NaluWind(bNaluWind, CudaPackage):
    depends_on('trilinos~shared+cuda+exodus+tpetra+muelu+belos+ifpack2+amesos2+zoltan+stk+boost~superlu-dist+superlu+hdf5+zlib+pnetcdf+shards~hypre@master,develop', when='+cuda')
    depends_on('kokkos-nvcc-wrapper', when='+cuda')

   # def setup_environment(self, spack_env, run_env):
   #     if '+cuda' in self.spec:
   #         spack_env.set('NVCC_WRAPPER_DEFAULT_COMPILER', spack_cxx)

   # def cmake_args(self):
   #     define = CMakePackage.define

   #     options = super(NaluWind, self).cmake_args()

   #     if '+cuda' in self.spec:
   #         options.append(
   #                 define('ENABLE_CUDA', True),
   #         )
   #         for opt in options:
   #             if "DCMAKE_CXX_COMPILER" in opt:
   #                 ind = options.index(opt)
   #                 options[ind] = define("CMAKE_CXX_COMPILER", self.spec['trilinos'].prefix + "/bin/nvcc_wrapper")

   #     return options
