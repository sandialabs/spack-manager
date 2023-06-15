# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack.package import *


class HpcxMpi(Package):
    """The HPC-X MPI implementation from NVIDIA/Mellanox based on OpenMPI.
    This package is for external specs only and for the Azure platform."""

    homepage = "https://developer.nvidia.com/networking/hpc-x"
    maintainers("mwkrentel")

    has_code = False

    provides("mpi")

    def install(self, spec, prefix):
        raise InstallError("HPC-X MPI is not buildable, it is for external " "specs only.")

    def setup_run_environment(self, env):
        env.set("MPICC", self.prefix.bin.mpicc)
        env.set("MPICXX", self.prefix.bin.mpicxx)
        env.set("MPIF77", self.prefix.bin.mpif77)
        env.set("MPIF90", self.prefix.bin.mpif90)
        env.prepend_path("LD_LIBRARY_PATH", self.prefix.lib)
        env.set("OPAL_PREFIX", self.prefix)
    
    def setup_dependent_build_environment(self, env, dependent_spec):
        self.setup_run_environment(env)
        env.set("OMPI_CC", spack_cc)
        env.set("OMPI_CXX", spack_cxx)
        env.set("OMPI_FC", spack_fc)
        env.set("OMPI_F77", spack_f77)

    def setup_dependent_package(self, module, dependent_spec):
        self.spec.mpicc = self.prefix.bin.mpicc
        self.spec.mpicxx = self.prefix.bin.mpicxx
        self.spec.mpifc = self.prefix.bin.mpif90
        self.spec.mpif77 = self.prefix.bin.mpif77
