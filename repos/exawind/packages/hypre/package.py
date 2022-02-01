from spack import *
from spack.pkg.builtin.hypre import Hypre as bHypre
import os

class Hypre(bHypre):
    def _configure_args(self):
        spec = self.spec
        options = super(Hypre, self)._configure_args()                        
                                                                           
        if '+cuda' in self.spec:
            options.append('--enable-cusparse')

        return options

    def setup_build_environment(self, env):
        spec = self.spec
        if '+mpi' in spec:
            env.set('CC', spec['mpi'].mpicc)
            env.set('CXX', spec['mpi'].mpicxx)
            if '+fortran' in spec:
                env.set('F77', spec['mpi'].mpif77)

        if '+cuda' in spec:
            env.set('CUDA_HOME', spec['cuda'].prefix)
            env.set('CUDA_PATH', spec['cuda'].prefix)
            cuda_arch = spec.variants['cuda_arch'].value
            if cuda_arch:
                arch_sorted = list(sorted(cuda_arch, reverse=True))
                env.set('HYPRE_CUDA_SM', arch_sorted[0])
            # In CUDA builds hypre currently doesn't handle flags correctly
            env.append_flags(
                'CXXFLAGS', '-O2')
            if '+debug' in spec:
                env.append_flags('CXXFLAGS', '-g')
