# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.builtin.nalu_wind import NaluWind as bNaluWind
from spack.pkg.builtin.kokkos import Kokkos
import os
from manager_cmds.find_machine import find_machine
from smpackages import *


def trilinos_version_filter(name):
    local = str(name)
    if "develop" in local:
        return local
    else:
        return "stable"

class NaluWind(SMCMakeExtension, bNaluWind, ROCmPackage):
    version("master", branch="master", submodules=True)
    version("multiphase", branch="multiphase_dev", submodules=True)

    variant("asan", default=False,
            description="Turn on address sanitizer")
    variant("fsi", default=False,
            description="Use FSI branch of openfast")
    variant("stk_simd", default=False,
            description="Enable SIMD in STK")
    variant("shared", default=True,
            description="Build shared libraries")
    variant("hypre2", default=False,
            description="Compile with namespaced Hypre support")
    variant("umpire", default=False,
            description="Enable Umpire")
    conflicts("+shared", when="+cuda",
             msg="invalid device functions are generated with shared libs and cuda")
    conflicts("+shared", when="+rocm",
             msg="invalid device functions are generated with shared libs and rocm")
    variant("gpu-aware-mpi", default=False,
            description="gpu-aware-mpi")

    conflicts("+cuda", when="+rocm")
    conflicts("+rocm", when="+cuda")
    conflicts("openfast@fsi", when="~fsi")
    conflicts("+hypre", when="+hypre2")
    depends_on("hypre+gpu-aware-mpi", when="+gpu-aware-mpi")

    depends_on("hypre2@2.18.2: ~int64+mpi~superlu-dist~shared", when="+hypre2")
    depends_on("hypre+umpire", when="+umpire")
    depends_on("trilinos gotype=long")
    depends_on("openfast@fsi+netcdf+cxx", when="+fsi")

    for _arch in ROCmPackage.amdgpu_targets:
        depends_on("trilinos@13.4.0.2022.10.27: ~shared+exodus+tpetra+zoltan+stk+boost~superlu-dist~superlu+hdf5+shards~hypre+gtest+rocm amdgpu_target={0}".format(_arch),
                   when="+rocm amdgpu_target={0}".format(_arch))
        depends_on("hypre+rocm amdgpu_target={0}".format(_arch), when="+hypre+rocm amdgpu_target={0}".format(_arch))

    cxxstd=["14", "17"]
    variant("cxxstd", default="17", values=cxxstd,  multi=False)
    variant("tests", default=True, description="Activate regression tests")
    variant("unit-tests", default=True, description="Activate unit tests")

    for std in cxxstd:
        depends_on("trilinos cxxstd=%s" % std, when="cxxstd=%s" % std)

    def setup_build_environment(self, env):
        if "~stk_simd" in self.spec:
            env.append_flags("CXXFLAGS", "-DUSE_STK_SIMD_NONE")
        if "+asan" in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}".format(join_path(self.package_dir, "blacklist.asan")))
            env.set("LSAN_OPTIONS", "suppressions={0}".format(join_path(self.package_dir, "sup.asan")))
            env.set("ASAN_OPTIONS", "detect_container_overflow=0")
        if "+cuda" in self.spec:
            env.set("CUDA_LAUNCH_BLOCKING", "1")
            env.set("CUDA_MANAGED_FORCE_DEVICE_ALLOC", "1")
            env.set("OMPI_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set("MPICH_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set("MPICXX_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
        if "+rocm" in self.spec:
            env.append_flags('CXXFLAGS', '-fgpu-rdc')

    def cmake_args(self):
        spec = self.spec
        cmake_options = super(NaluWind, self).cmake_args()
        cmake_options.append(self.define_from_variant("CMAKE_CXX_STANDARD", "cxxstd"))
        cmake_options.append(self.define_from_variant("BUILD_SHARED_LIBS", "shared"))

        if find_machine(verbose=False) == "eagle" and "%intel" in spec:
            cmake_options.append(self.define("ENABLE_UNIT_TESTS", False))

        if find_machine(verbose=False) == "crusher":
            cmake_options.append(self.define("MPIEXEC_EXECUTABLE", "srun"))
            cmake_options.append(self.define("MPIEXEC_NUMPROC_FLAG", "--ntasks"))

        if spec.satisfies("dev_path=*"):
            cmake_options.append(self.define("CMAKE_EXPORT_COMPILE_COMMANDS",True))
            cmake_options.append(self.define("ENABLE_TESTS", True))

        if "+umpire" in spec:
            cmake_options.append(self.define_from_variant("ENABLE_UMPIRE", "umpire"))
            cmake_options.append(self.define("UMPIRE_DIR", spec["umpire"].prefix))

        if "+rocm" in spec:
            cmake_options.append(self.define("CMAKE_CXX_COMPILER", spec["hip"].hipcc))
            cmake_options.append(self.define("ENABLE_ROCM", True))
            targets = spec.variants["amdgpu_target"].value
            cmake_options.append(self.define("GPU_TARGETS", ";".join(str(x) for x in targets)))

        if "+hypre2" in spec:
            cmake_options.append(self.define("ENABLE_HYPRE", True))
            cmake_options.append(self.define("HYPRE_DIR", spec["hypre2"].prefix))

        if spec["mpi"].name == "openmpi":
            cmake_options.append(self.define("MPIEXEC_PREFLAGS", "--oversubscribe"))

        cmake_options.append(self.define_from_variant("ENABLE_OPENFAST_FSI", "fsi"))
        if "+fsi" in spec:
            cmake_options.append(self.define("OpenFAST_DIR", spec["openfast"].prefix))
            cmake_options.append(self.define("ENABLE_OPENFAST", True))

        if spec.satisfies("+tests") or self.run_tests or spec.satisfies("dev_path=*"):
            spack_manager_local_golds = os.path.join(os.getenv("SPACK_MANAGER"), "golds")
            spack_manager_golds_dir = os.getenv("SPACK_MANAGER_GOLDS_DIR", default=spack_manager_local_golds)
            if "+snl" in spec:
                spack_manager_golds_dir = "{}-{}".format(spack_manager_golds_dir, trilinos_version_filter(spec["trilinos"].version))

            saved_golds = os.path.join(spack_manager_golds_dir, "tmp", "nalu-wind")
            current_golds = os.path.join(spack_manager_golds_dir, "current", "nalu-wind")
            os.makedirs(saved_golds, exist_ok=True)
            os.makedirs(current_golds, exist_ok=True)
            cmake_options.append(self.define("NALU_WIND_SAVE_GOLDS", True))
            cmake_options.append(self.define("NALU_WIND_SAVED_GOLDS_DIR", saved_golds))
            cmake_options.append(self.define("NALU_WIND_REFERENCE_GOLDS_DIR", current_golds))

        return cmake_options
