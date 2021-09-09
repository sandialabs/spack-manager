from spack.pkg.builtin.trilinos import Trilinos as bTrilinos
import os

class Trilinos(bTrilinos):
    if os.environ['SPACK_MANAGER_MACHINE'] != 'summit':
        depends_on('ninja', type='build')
        generator = 'Ninja'

    def setup_build_environment(self, env):
        spec = self.spec
        if '+cuda' in spec and '+wrapper' in spec:
            if '+mpi' in spec:
                env.set('OMPI_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
                env.set('MPICH_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
                env.set('MPICXX_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            else:
                env.set('CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
        # Workaround for segfaults with IPO
        if '%intel' in spec and '+stk' in spec:
            for cc in "CXX C F LD".split():
                env.append_flags(cc + "FLAGS", '-no-ipo')

