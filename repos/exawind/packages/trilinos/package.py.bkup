from spack import *
from spack.pkg.builtin.trilinos import Trilinos as bTrilinos

class Trilinos(bTrilinos, CudaPackage):
    # cuda stuff from PR #17900
    variant('cuda', default=True, description="add cuda")
    conflicts('+cuda', when='~tpetra')

    def setup_build_environment(self, env):
       spec = self.spec
       env.set('CUDA_WRAPPER', self.prefix.bin + "/nvcc_wrapper")
       env.set('CUDA_LAUNCH_BLOCKING', True)
       env.set('CUDA_MANAGED_FORCE_DEVICE_ALLOC', True)
       env.set('TPETRA_ASSUME_CUDA_AWARE_MPI', False)
       env.set('NVCC_WRAPPER_DEFAULT_COMPILER', spack_cxx)
       env.set('OMPI_CXX', self.prefix.bin + '/nvcc_wrapper')
       env.set('CXX', spec['mpi'].mpicxx)

    def setup_dependent_build_environment(self, env, dependent_spec):
        self.setup_build_environment(env)
        
    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define

        blas = spec['blas'].libs
        lapack = spec['lapack'].libs

        options = []
        options.extend([
            define("Kokkos_CXX_STANDARD","11"),
            define("Kokkos_ARCH_SKX",True),
            define("Kokkos_ARCH_VOLTA70",True),
            define("KOKKOS_ENABLE_PRAGMA_IVDEP",True),
            define("KOKKOS_ENABLE_PRAGMA_LOOPCOUNT",True),
            define("KOKKOS_ENABLE_PRAGMA_SIMD",True),
            define("KOKKOS_ENABLE_PRAGMA_UNROLL",True),
            define("KOKKOS_ENABLE_PRAGMA_VECTOR",True),
            define("Kokkos_ENABLE_AGGRESSIVE_VECTORIZATION", True),
            define("MPI_USE_COMPILER_WRAPPERS",True),
            define("MPI_CXX_COMPILER",spec['mpi'].mpicxx),
            define("MPI_C_COMPILER",spec['mpi'].mpicc),
            define("Trilinos_ENABLE_OPENMP",False),
            define("Kokkos_ENABLE_OPENMP",False),
            define("Tpetra_INST_OPENMP",False),
            define("Trilinos_ENABLE_CUDA",True),
            define("TPL_ENABLE_CUDA",True),
            define("Kokkos_ENABLE_CUDA",True),
            define("Kokkos_ENABLE_CUDA_UVM",True),
            define("Kokkos_ENABLE_CUDA_CONSTEXPR",True),
            define("Tpetra_ENABLE_CUDA",True),
            define("Tpetra_INST_CUDA",True),
            define("Tpetra_ASSUME_CUDA_AWARE_MPI", False),
            define("Kokkos_ENABLE_CUDA_LAMBDA",True),
            define("Kokkos_ENABLE_CUDA_RELOCATABLE_DEVICE_CODE",True),
            define("Kokkos_ENABLE_DEPRECATED_CODE", False),
            define("Kokkos_ENABLE_COMPLEX", False),
            define("Tpetra_INST_SERIAL",True),
            define("Trilinos_ENABLE_EXPLICIT_INSTANTIATION", True),
            define("Tpetra_INST_DOUBLE",True),
            define("Tpetra_INST_INT_LONG_LONG", True),
            define("Tpetra_INST_COMPLEX_DOUBLE", False),
            define("Trilinos_ENABLE_TESTS", False),
            define("Trilinos_ENABLE_ALL_OPTIONAL_PACKAGES", False),
            define("Trilinos_ASSERT_MISSING_PACKAGES", False),
            define("Trilinos_ALLOW_NO_PACKAGES", False),
            define("Trilinos_ENABLE_Epetra", False),
            define("Trilinos_ENABLE_Tpetra",True),
            define("Trilinos_ENABLE_KokkosKernels",True),
            define("Trilinos_ENABLE_ML", False),
            define("Trilinos_ENABLE_MueLu",True),
            define("Xpetra_ENABLE_Kokkos_Refactor",True),
            define("MueLu_ENABLE_Kokkos_Refactor",True),
            define("MueLu_ENABLE_Experimental",True),
            define("Xpetra_ENABLE_Experimental",True),
            define("Trilinos_ENABLE_EpetraExt", False),
            define("Trilinos_ENABLE_AztecOO", False),
            define("Trilinos_ENABLE_Belos",True),
            define("Trilinos_ENABLE_Ifpack2",True),
            define("Trilinos_ENABLE_Amesos2",True),
            define("Amesos2_ENABLE_SuperLU",True),
            define("Trilinos_ENABLE_Zoltan2",True),
            define("Trilinos_ENABLE_Ifpack", False),
            define("Trilinos_ENABLE_Amesos", False),
            define("Trilinos_ENABLE_Zoltan",True),
            define("Trilinos_ENABLE_STK",True),
            define("Trilinos_ENABLE_Gtest",True),
            define("Trilinos_ENABLE_STKClassic", False),
            define("Trilinos_ENABLE_STKExprEval",True),
            define("Trilinos_ENABLE_SEACASExodus",True),
            define("Trilinos_ENABLE_SEACASEpu",True),
            define("Trilinos_ENABLE_SEACASExodiff",True),
            define("Trilinos_ENABLE_SEACASNemspread",True),
            define("Trilinos_ENABLE_SEACASNemslice",True),
            define("Trilinos_ENABLE_SEACASIoss",True),
            define("TPL_ENABLE_MPI",True),
            define("TPL_ENABLE_Boost",True),
            define("BoostLib_INCLUDE_DIRS", spec['boost'].prefix.include),
            define("BoostLib_LIBRARY_DIRS", spec['boost'].prefix.lib),
            define("Boost_INCLUDE_DIRS", spec['boost'].prefix.include),
            define("Boost_LIBRARY_DIRS", spec['boost'].prefix.lib),
            define("TPL_ENABLE_SuperLU", True),
            define("SuperLU_INCLUDE_DIRS", spec['superlu'].prefix.include),
            define("SuperLU_LIBRARY_DIRS", spec['superlu'].prefix.lib),
            define("TPL_ENABLE_Netcdf",True),
            define("NetCDF_ROOT",spec['netcdf-c'].prefix),
            define("TPL_Netcdf_PARALLEL",True),
            define("TPL_Netcdf_Enables_Netcdf4",True),
            define("TPL_ENABLE_Pnetcdf",True),
            define("PNetCDF_ROOT",spec['parallel-netcdf'].prefix),
            define("Pnetcdf_INCLUDE_DIRS", spec['parallel-netcdf'].prefix.include),
            define("Pnetcdf_LIBRARY_DIRS", spec['parallel-netcdf'].prefix.lib),
            define("TPL_ENABLE_HDF5",True),
            define("HDF5_ROOT",spec['hdf5'].prefix),
            define("HDF5_NO_SYSTEM_PATHS",True),
            define("TPL_ENABLE_Zlib",True),
            define("Zlib_INCLUDE_DIRS",spec['zlib'].prefix.include),
            define("Zlib_LIBRARY_DIRS",spec['zlib'].prefix.lib),
            define("BLAS_LIBRARY_NAMES", ';'.join(blas.names)),
            define("LAPACK_LIBRARY_NAMES", ';'.join(lapack.names)),
        ])



        return options
