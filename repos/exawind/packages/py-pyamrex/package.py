# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyPyamrex(PythonPackage):
    """Python bindings for AMReX library."""

    git = "https://github.com/Exawind/pyamrex.git"

    version('master', branch='master')

    # Currently requires manually copying __init__.py and *.pxi files from source directory into installation directory

    depends_on('python@3.3:', type=('build', 'link', 'run'))
    depends_on('py-scikit-build')
    depends_on('py-mpi4py')
    depends_on('py-cython@0.25.1:')
    depends_on('py-numpy')
    depends_on('mpi')
    depends_on('amrex+hypre+linear_solvers+mpi')
    depends_on('cmake', type=('build'))
