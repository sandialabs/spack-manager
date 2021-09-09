import os
from spack import *
from spack.pkg.builtin.kokkos_nvcc_wrapper import KokkosNvccWrapper as bKokkosNvccWrapper

class KokkosNvccWrapper(bKokkosNvccWrapper):
    def setup_dependent_build_environment(self, env, dependent_spec):
        wrapper = join_path(self.prefix.bin, "nvcc_wrapper")
        env.set('CUDA_ROOT', dependent_spec["cuda"].prefix)
        env.set('NVCC_WRAPPER_DEFAULT_COMPILER', self.compiler.cxx)
        env.set('KOKKOS_CXX', self.compiler.cxx)
        env.set('MPICH_CXX', wrapper)
        env.set('OMPI_CXX', wrapper)
        env.set('MPICXX_CXX', wrapper)

