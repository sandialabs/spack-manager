# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class H5zZfp(CMakePackage):
    """A highly flexible floating point and integer compression plugin for the
       HDF5 library using ZFP compression."""

    homepage = "https://h5z-zfp.readthedocs.io/en/latest"
    git      = "https://github.com/LLNL/H5Z-ZFP.git"
    url      = "https://github.com/LLNL/H5Z-ZFP/archive/refs/tags/v1.0.1.tar.gz"

    version("develop", branch="master", preferred=True)

    variant("fortran", default=False, description="Enable Fortran support")

    depends_on("hdf5+fortran", when="+fortran")
    depends_on("hdf5",         when="~fortran")
    depends_on("mpi",          when="^hdf5+mpi")
    depends_on("zfp bsws=8")

    patch("skip_add_library.patch")

    def cmake_args(self):
        args = [
            self.define_from_variant("FORTRAN_INTERFACE", "fortran")
        ]

        if "^hdf5+mpi" in self.spec:
            args.append(self.define("CMAKE_C_COMPILER",
                                    self.spec["mpi"].mpicc))
            if "+fortran" in self.spec:
                args.append(self.define("CMAKE_Fortran_COMPILER",
                                        self.spec["mpi"].mpifc))

        return args
