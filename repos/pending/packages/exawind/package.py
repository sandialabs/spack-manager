# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Exawind(CMakePackage, CudaPackage):
    """Multi-application driver for Exawind project."""

    homepage = "https://github.com/Exawind/exawind-driver"
    git = "https://github.com/Exawind/exawind-driver.git"

    maintainers = ['jrood-nrel']

    tags = ['ecp', 'ecp-apps']

    version('master', branch='main')

    variant('openfast', default=False,
            description='Enable OpenFAST integration')

    depends_on('tioga+shared~nodegid')
    depends_on('trilinos+stk')
    depends_on('nalu-wind+fftw+hypre+tioga+wind-utils')
    depends_on('amr-wind+hypre+mpi+netcdf')
    depends_on('yaml-cpp@0.6:')

    depends_on('nalu-wind+openfast', when='+openfast')
    depends_on('amr-wind+openfast', when='+openfast')
    depends_on('openfast+cxx+shared@2.6.0', when='+openfast')

    for arch in CudaPackage.cuda_arch_values:
        depends_on('nalu-wind+cuda cuda_arch=%s' % arch, when='+cuda cuda_arch=%s' % arch)
        depends_on('amr-wind+cuda cuda_arch=%s' % arch, when='+cuda cuda_arch=%s' % arch)
        depends_on('trilinos+cuda cuda_arch=%s' % arch, when='+cuda cuda_arch=%s' % arch)

    def cmake_args(self):
        spec = self.spec

        args = [
            self.define('Trilinos_DIR', spec['trilinos'].prefix),
            self.define('TIOGA_DIR', spec['tioga'].prefix),
            self.define('Nalu-Wind_DIR', spec['nalu-wind'].prefix),
            self.define('AMR-Wind_DIR', spec['amr-wind'].prefix),
            self.define('YAML-CPP_DIR', spec['yaml-cpp'].prefix)
        ]

        if '+openfast' in spec:
            args.append(self.define('OpenFAST_DIR', spec['openfast'].prefix))

        return args
