# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.builtin.trilinos import Trilinos as bTrilinos
import os
import manager_cmds.find_machine as fm
from manager_cmds.find_machine import find_machine
from smpackages import *

class Trilinos(bTrilinos, SMCMakeExtension):
    # Our custom release versions should be the latest release tag found on
    # the trilinos github page appended with the date of the commit.
    # this preserves the Trilinos versioning scheme and will allow for valid
    # version comparisons in spack's internals.
    version("13.4.0.2023.02.28", commit="8b3e2e1db4c7e07db13225c73057230c4814706f")
    version("13.4.0.2022.10.27", commit="da54d929ea62e78ba8e19c7d5aa83dc1e1f767c1")
    version("13.2.0.2022.06.05", commit="7498bcb9b0392c830b83787f3fb0c17079431f06")
    variant("stk_unit_tests", default=False,
            description="turn on STK unit tests")
    variant("stk_simd", default=False,
            description="Enable SIMD in STK")
    variant("asan", default=False,
            description="Turn on address sanitizer")
    variant("pic", default=True,
            description="Position independent code")

    patch("kokkos_zero_length_team.patch", when="@:13.3.0")
    patch("rocm_seacas.patch", when="@develop+rocm")
    patch("kokkos_hip_subview.patch", when="@develop+rocm")

    if find_machine(verbose=False, full_machine_name=False) == "eagle":
        patch("stk-coupling-versions-func-overload.patch", when="@13.3.0:13.4.0.2022.12.15")

    def setup_build_environment(self, env):
        spec = self.spec
        if "+cuda" in spec and "+wrapper" in spec:
            if spec.variants["build_type"].value == "RelWithDebInfo" or spec.variants["build_type"].value == "Debug":
                env.append_flags("CXXFLAGS", "-Xcompiler -rdynamic -lineinfo")
            if "+mpi" in spec:
                env.set("OMPI_CXX", spec["kokkos-nvcc-wrapper"].kokkos_cxx)
                env.set("MPICH_CXX", spec["kokkos-nvcc-wrapper"].kokkos_cxx)
                env.set("MPICXX_CXX", spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            else:
                env.set("CXX", spec["kokkos-nvcc-wrapper"].kokkos_cxx)

        if "+rocm" in spec:
            if "+mpi" in spec:
                env.set("OMPI_CXX", self.spec["hip"].hipcc)
                env.set("MPICH_CXX", self.spec["hip"].hipcc)
                env.set("MPICXX_CXX", self.spec["hip"].hipcc)
            else:
                env.set("CXX", self.spec["hip"].hipcc)
            if "+stk" in spec:
                # Using CXXFLAGS for hipcc which doesn't use flags in the spack wrappers
                env.append_flags("CXXFLAGS", "-DSTK_NO_BOOST_STACKTRACE")
                if "~stk_simd" in spec:
                    env.append_flags("CXXFLAGS", "-DUSE_STK_SIMD_NONE")

        if "+asan" in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer")
            env.set("LSAN_OPTIONS", "suppressions={0}".format(join_path(self.package_dir, "sup.asan")))

    def setup_dependent_package(self, module, dependent_spec):
        if "+wrapper" in self.spec:
            # Hardcode nvcc_wrapper path to avoid kokkos-nvcc-wrapper error with trilinos as an external
            self.spec.kokkos_cxx = os.path.join(os.getenv("SPACK_MANAGER"), "bin", "nvcc_wrapper")
        else:
            self.spec.kokkos_cxx = spack_cxx

    def flag_handler(self, name, flags):
        base_flags = bTrilinos.flag_handler(self, name, flags)
        if find_machine(verbose=False, full_machine_name=False) == "perlmutter":
            expt_lambda_flag = "--expt-extended-lambda"
            if expt_lambda_flag in base_flags[0]:
                updated_flags = base_flags[0].remove(expt_lambda_flag)
                return (updated_flags, None, None)
        return base_flags

    def cmake_args(self):
        spec = self.spec
        options = super(Trilinos, self).cmake_args()

        options.append(self.define_from_variant("CMAKE_POSITION_INDEPENDENT_CODE", "pic"))
        options.append(self.define("Trilinos_ENABLE_SEACAS", True))
        options.append(self.define("Trilinos_ENABLE_SEACASCpup", False))
        options.append(self.define("Trilinos_ENABLE_SEACASEjoin", False))
        options.append(self.define("Trilinos_ENABLE_SEACASExo_format", False))
        options.append(self.define("Trilinos_ENABLE_SEACASExomatlab", False))
        options.append(self.define("Trilinos_ENABLE_SEACASNas2exo", False))
        options.append(self.define("Trilinos_ENABLE_SEACASSlice", False))
        options.append(self.define("Trilinos_ENABLE_SEACASuplib", False))
        options.append(self.define("Trilinos_ENABLE_SEACASuplibC", False))
        options.append(self.define("Trilinos_ENABLE_SEACASuplibCpp", False))
        options.append(self.define("Trilinos_ENABLE_SEACASZellij", False))

        if "+stk" in spec:
            options.append(self.define_from_variant("STK_ENABLE_TESTS", "stk_unit_tests"))
            options.append(self.define("SEACAS_ENABLE_SEACASSupes", False))
            options.append(self.define("Trilinos_ENABLE_SEACASSupes", False))

        if "+rocm" in self.spec:
            # Used as an optimization to only list the single specified
            # arch in the offload-arch compile line, but not explicitly necessary
            targets = self.spec.variants["amdgpu_target"].value
            options.append(self.define("CMAKE_HIP_ARCHITECTURES", ";".join(str(x) for x in targets)))
            options.append(self.define("AMDGPU_TARGETS", ";".join(str(x) for x in targets)))
            options.append(self.define("GPU_TARGETS", ";".join(str(x) for x in targets)))
            options.append(self.define("TPL_ENABLE_Boost", False))
            options.append(self.define("Trilinos_ENABLE_ALL_OPTIONAL_PACKAGES", False))
            options.append(self.define("Trilinos_ALLOW_NO_PACKAGES", False))
            options.append(self.define("Trilinos_ASSERT_MISSING_PACKAGES", False))
            options.append(self.define("Trilinos_ENABLE_Fortran", False))
            # Kokkos
            options.append(self.define("Trilinos_ENABLE_Kokkos", True))
            options.append(self.define("Kokkos_ENABLE_HIP", True))
            options.append(self.define("Kokkos_ARCH_ZEN2", False))
            options.append(self.define("Kokkos_ARCH_ZEN3", True))
            options.append(self.define("Kokkos_ARCH_VEGA90A", True))
            options.append(self.define("Kokkos_ENABLE_HIP_RELOCATABLE_DEVICE_CODE", True))
            # Tests
            options.append(self.define("SEACASExodus_ENABLE_TESTS", False))
            options.append(self.define("SEACASIoss_ENABLE_TESTS", False))
            options.append(self.define("SEACASNemesis_ENABLE_TESTS", False))
            options.append(self.define("SEACASEpu_ENABLE_TESTS", False))
            options.append(self.define("SEACASExodiff_ENABLE_TESTS", False))
            options.append(self.define("SEACASNemspread_ENABLE_TESTS", False))
            options.append(self.define("SEACASNemslice_ENABLE_TESTS", False))
            options.append(self.define("SEACASChaco_ENABLE_TESTS", False))
            options.append(self.define("SEACASAprepro_ENABLE_TESTS", False))

            options.append(self.define("Trilinos_ENABLE_TESTS", False))
            options.append(self.define("Ifpack2_ENABLE_TESTS", False))
            options.append(self.define("MueLu_ENABLE_TESTS", False))
            options.append(self.define("PanzerMiniEM_ENABLE_TESTS", False))
            options.append(self.define("Tpetra_INST_HIP", True))
            options.append(self.define("Tpetra_ENABLE_TESTS", False))
            # STK
            options.append(self.define("Trilinos_ENABLE_STK", True))
            options.append(self.define_from_variant("STK_ENABLE_TESTS", "stk_unit_tests"))
            options.append(self.define("Trilinos_ENABLE_STKMesh", True))
            options.append(self.define("Trilinos_ENABLE_STKIO", True))
            options.append(self.define("Trilinos_ENABLE_STKBalance", True))
            options.append(self.define("Trilinos_ENABLE_STKMath", True))
            options.append(self.define("Trilinos_ENABLE_STKSearch", True))
            options.append(self.define("Trilinos_ENABLE_STKTransfer", True))
            options.append(self.define("Trilinos_ENABLE_STKTopology", True))
            options.append(self.define("Trilinos_ENABLE_STKUtils", True))
            options.append(self.define("Trilinos_ENABLE_STKTools", True))

        return options
