# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *


class PyStk(PythonPackage):
    """pySTK is a Python/Cython wrapper to provide a python interface to STK"""

    homepage = "https://sayerhs.github.io/pystk"
    git = "https://github.com/sayerhs/pystk.git"
    url = "https://github.com/sayerhs/pystk.git"

    maintainers = ["psakievich"]

    version("master", branch="master")

    depends_on("trilinos+stk")
    depends_on("py-cython", type="build")
    depends_on("py-scikit-build", type="build")
    depends_on("cmake@3.13:", type="build")

    depends_on("python@3.5:")
    depends_on("py-numpy")
