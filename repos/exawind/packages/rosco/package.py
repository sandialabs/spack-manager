# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Rosco(CMakePackage):
    """
    ROSCO controls package for OpenFAST from NREL
    Note: this only builds ROSCO controls library for inclusion with OpenFAST
    If the toolbox or tuning scripts are needed, please build manually
    """

    homepage = "https://rosco.readthedocs.io/en/latest/"
    git = "https://github.com/NREL/ROSCO.git"

    maintainers("dzalkind","ndevelder")

    version("develop", branch="develop")
    version("main", branch="main")
    version("2.8.0", tag="v2.8.0")
    version("2.7.0", tag="v2.7.0")
    version("2.6.0", tag="v2.6.0")
    version("2.5.1", tag="v2.5.1")
    version("2.5.0", tag="v2.5.0")
    version("2.4.1", tag="v2.4.1")
    version("2.4.0", tag="v2.4.0")
    version("2.3.0", tag="v2.3.0")
    version("2.2.0", tag="v2.2.0")


    variant("shared", default=False, description="Build shared libraries")
    variant("pic", default=False, description="Position independent code")

    # Dependencies for OpenFAST Fortran
    # depends_on("openfast")

    root_cmakelists_dir = 'ROSCO'

    def cmake_args(self):
        spec = self.spec

        options = []

        options.extend(
            [
                self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
                self.define_from_variant("CMAKE_POSITION_INDEPENDENT_CODE", "pic"),
            ]
        )

        return options

    def setup_run_environment(self, env):
        env.set('ROSCO_DISCON', self.prefix.lib + "/libdiscon.so")
        env.set('ROSCO_DISCON_DIR', self.prefix.lib)

    def flag_handler(self, name, flags):
        if name == "fflags" and self.compiler.fc.endswith("gfortran"):
            flags.extend(["-ffree-line-length-0"])

        return (None, None, flags)