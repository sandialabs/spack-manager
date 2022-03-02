from spack import *
from spack.pkg.builtin.hypre import Hypre as bHypre
import os

class HypreMixed(bHypre, ROCmPackage):

    conflicts('+rocm', when='+int64')
    conflicts('+rocm', when='@:2.23.0')
    conflicts('+unified-memory', when='~cuda~rocm')

    def _configure_args(self):
        spec = self.spec
        options = super(Hypre, self)._configure_args()

        if '+cuda' in self.spec:
            options.append('--enable-cusparse')

        if '+rocm' in spec:
            configure_args.extend([
                '--with-hip',
                '--enable-rocrand',
                '--enable-rocsparse',
            ])
            rocm_arch_vals = spec.variants['amdgpu_target'].value
            if rocm_arch_vals:
                rocm_arch_sorted = list(sorted(rocm_arch_vals, reverse=True))
                rocm_arch = rocm_arch_sorted[0]
                configure_args.append('--with-gpu-arch={0}'.format(rocm_arch))
        else:
            configure_args.extend([
                '--without-hip',
                '--disable-rocrand',
                '--disable-rocsparse',
            ])

        return options
