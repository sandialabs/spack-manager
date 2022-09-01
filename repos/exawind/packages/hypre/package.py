from spack import *
from spack.pkg.builtin.hypre import Hypre as bHypre
import os

class Hypre(bHypre):

    phases = ['autoreconf', 'distclean', 'configure', 'clean', 'build', 'install']

    variant('gpu-aware-mpi', default=False, description='Use gpu-aware mpi')
    variant('rocblas', default=False, description='use rocblas')
    variant('cublas', default=False, description='use cublas')
    conflicts('+cublas', when='~cuda', msg='cublas requires cuda to be enabled')
    conflicts('+rocblas', when='~rocm', msg='rocblas requires rocm to be enabled')
    variant('umpire', default=False, description='Use Umpire')
    depends_on("umpire", when='+umpire')
    depends_on("umpire+rocm", when='+umpire+rocm')
    depends_on("umpire+cuda", when='+umpire+cuda')

    def distclean(self, spec, prefix):
        with working_dir('src'):
            if 'SPACK_MANAGER_CLEAN_HYPRE' in os.environ:
                make('distclean')

    def clean(self, spec, prefix):
        with working_dir('src'):
            if 'SPACK_MANAGER_CLEAN_HYPRE' in os.environ:
                make('clean')

    def configure_args(self):
        spec = self.spec
        options = super(Hypre, self).configure_args()

        if '+gpu-aware-mpi' in spec:
            options.append('--enable-gpu-aware-mpi')

        if '+rocblas' in spec:
            options.append('--enable-rocblas')

        if '+cublas' in spec:
            options.append('--enable-cublas')

        if '+umpire' in spec:
            if  (('+cuda' in spec or '+rocm' in spec) and "--enable-device-memory-pool" in options):
                options.remove("--enable-device-memory-pool")
            options.append('--with-umpire')
            options.append('--with-umpire-pinned')
            options.append('--with-umpire-include=%s'%(spec['umpire'].prefix.include))
            options.append('--with-umpire-lib-dirs=%s'%(spec['umpire'].prefix.lib))
            options.append('--with-umpire-libs=umpire')

        return options
