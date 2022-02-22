# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class HypreMiniApp(CMakePackage, CudaPackage, ROCmPackage):
    """HYPRE mini-app for use with Nalu-Wind linear systems. """

    homepage = "https://github.com/Exawind/hypre-mini-app"
    git      = "https://github.com/Exawind/hypre-mini-app.git"

    maintainers = ['jrood-nrel']

    tags = ['ecp', 'ecp-apps']

    version('master', branch='master', submodules=True)

    variant('umpire', default=False,
            description='Enable Umpire')

    depends_on('mpi')
    depends_on('hypre+mpi@2.20.0:')
    depends_on('yaml-cpp@0.6.2:')
    depends_on('umpire', when='+umpire')
    for arch in CudaPackage.cuda_arch_values:
        depends_on('hypre+cuda cuda_arch=%s @2.20.0:' % arch,
                   when='+cuda cuda_arch=%s' % arch)
    for arch in ROCmPackage.amdgpu_targets:
        depends_on('hypre+rocm amdgpu_target=%s' % arch,
                   when='+rocm amdgpu_target=%s' % arch)

    def cmake_args(self):
        args = [
            self.define('HYPRE_DIR', spec['hypre'].prefix),
            self.define('YAML_ROOT_DIR', spec['yaml-cpp'].prefix),
            self.define_from_variant('ENABLE_CUDA', 'cuda'),
            self.define_from_variant('ENABLE_HIP', 'rocm'),
        ]

        args.append(self.define_from_variant('ENABLE_UMPIRE', 'umpire'))
        if '+umpire' in spec:
            args.append(self.define('UMPIRE_DIR', spec['umpire'].prefix))

        return args
