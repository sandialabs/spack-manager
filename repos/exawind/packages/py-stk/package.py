# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
from spack import *


class PyStk(PythonPackage):
    """pySTK is a Python/Cython wrapper to provide a python interface to STK"""

    homepage = "https://sayerhs.github.io/pystk"
    git      = "https://github.com/sayerhs/pystk.git"
    url      = "https://github.com/sayerhs/pystk.git"

    maintainers = ['sayerhs','psakievich']

    version('master', branch='master')

    depends_on('trilinos+stk')
    depends_on('py-cython', type='build')
    depends_on('py-scikit-build', type='build')
    depends_on('cmake@3.13:', type='build')

    depends_on('python@3.5:')
    depends_on('py-numpy')
