# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyPystk(PythonPackage):
    """Python bindings for Sierra Toolkit library."""

    git = "https://github.com/Exawind/pystk.git"

    version('master', branch='master')

    # Currently requires manually copying __init__.py files from source directory into installation directory

    depends_on('python@3.5:', type=('build', 'link', 'run'))
    depends_on('trilinos+stk')
    depends_on('py-scikit-build')
    depends_on('py-cython@0.25.1:')
    depends_on('py-numpy')
    depends_on('mpi')
    depends_on('cmake', type=('build'))
