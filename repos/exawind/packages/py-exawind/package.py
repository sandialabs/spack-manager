# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyExawind(PythonPackage):
    """Application suite and Python driver for Exawind project."""

    homepage = "https://github.com/Exawind"
    git = "https://github.com/Exawind/exawind-sim.git"

    maintainers = ['jrood-nrel']

    tags = ['ecp', 'ecp-apps']

    version('master', branch='master')

    # Currently requires manually copying __init__.py files from source directory into installation directory

    # The Exawind python driver loads shared libraries
    depends_on('nalu-wind+fftw+hypre+openfast+tioga+wind-utils')
    depends_on('amr-wind+hypre+mpi+netcdf+openfast')
    depends_on('amrex')
    depends_on('tioga+shared~nodegid')
    depends_on('openfast+cxx+shared@master')
    depends_on('trilinos+stk')
    depends_on('py-pystk')
    depends_on('py-pyamrex')
    depends_on('py-mpi4py')
    depends_on('py-pyyaml')
    depends_on('py-cython@0.25.1:')
    depends_on('py-numpy')
    depends_on('py-pandas')
    depends_on('py-ipython')
    depends_on('py-scikit-build')
    depends_on('mpi')
    depends_on('cmake', type=('build'))

    def setup_run_environment(self, env):
        env.set('TRILINOS_ROOT_DIR', self.spec['trilinos'].prefix)
        env.set('AMR_WIND_ROOT_DIR', self.spec['amr-wind'].prefix)
        env.set('TIOGA_ROOT_DIR', self.spec['tioga'].prefix)
        env.set('AMREX_ROOT_DIR', self.spec['amrex'].prefix)
        env.set('NALU_WIND_ROOT_DIR', self.spec['nalu-wind'].prefix)
