# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
#from spack.pkg.builtin.exawind import Exawind as bExawind
from shutil import copyfile
import os
from smpackages import *


class Exawind(SMCMakeExtension, CudaPackage, ROCmPackage):
    """Multi-application driver for Exawind project."""

    homepage = "https://github.com/Exawind/exawind-driver"
    git = "https://github.com/Exawind/exawind-driver.git"

    maintainers = ["jrood-nrel"]

    tags = ["ecp", "ecp-apps"]

    # Testing is currently always enabled, but should be optional in the future
    # to avoid cloning the mesh submodule
    version("master", branch="main", submodules=True)
    version("multiphase", branch="multiphase_dev", submodules=True)

    variant("asan", default=False,
            description="turn on address sanitizer")
    variant("openfast", default=False,
            description="Enable OpenFAST integration")
    variant("fsi", default=False,
            description="Enable OpenFAST FSI integration")
    variant("hypre", default=True,
            description="Enable hypre solver")
    variant("amr_wind_gpu", default=False,
            description="Enable AMR-Wind on the GPU")
    variant("nalu_wind_gpu", default=False,
            description="Enable Nalu-Wind on the GPU")
    variant("stk_simd", default=False,
            description="Enable SIMD in STK")
    variant("umpire", default=False,
            description="Enable Umpire")
    variant("tiny_profile", default=False,
            description="Turn on AMR-wind with tiny profile")
    variant("sycl", default=False,
            description="Enable SYCL backend for AMR-Wind")
    variant("gpu-aware-mpi", default=False,
            description="gpu-aware-mpi")

    conflicts("+amr_wind_gpu", when="~cuda~rocm~sycl")
    conflicts("+nalu_wind_gpu", when="~cuda~rocm")
    conflicts("+nalu_wind_gpu", when="+sycl")

    for arch in CudaPackage.cuda_arch_values:
        depends_on("amr-wind+cuda cuda_arch=%s" % arch, when="+amr_wind_gpu+cuda cuda_arch=%s" % arch)
        depends_on("nalu-wind+cuda cuda_arch=%s" % arch, when="+nalu_wind_gpu+cuda cuda_arch=%s" % arch)
        depends_on("trilinos+cuda cuda_arch=%s" % arch, when="+nalu_wind_gpu+cuda cuda_arch=%s" % arch)

    for arch in ROCmPackage.amdgpu_targets:
        depends_on("amr-wind+rocm amdgpu_target=%s" % arch, when="+amr_wind_gpu+rocm amdgpu_target=%s" % arch)
        depends_on("nalu-wind+rocm amdgpu_target=%s" % arch, when="+nalu_wind_gpu+rocm amdgpu_target=%s" % arch)
        depends_on("trilinos+rocm amdgpu_target=%s" % arch, when="+nalu_wind_gpu+rocm amdgpu_target=%s" % arch)

    depends_on("nalu-wind+tioga")
    depends_on("amr-wind+netcdf+mpi")
    depends_on("tioga~nodegid")
    depends_on("yaml-cpp@0.6:")
    depends_on("nalu-wind+openfast", when="+openfast")
    depends_on("nalu-wind+fsi", when="+fsi")
    depends_on("openfast+cxx@2.6.0:", when="+openfast")
    depends_on("openfast+cxx@2.6.0:", when="^nalu-wind+openfast")
    depends_on("openfast+cxx@2.6.0:", when="^amr-wind+openfast")
    depends_on("nalu-wind+hypre~hypre2", when="+hypre+amr_wind_gpu+nalu_wind_gpu")
    depends_on("nalu-wind+hypre~hypre2", when="+hypre~amr_wind_gpu~nalu_wind_gpu")
    depends_on("nalu-wind+hypre2~hypre", when="+hypre~amr_wind_gpu+nalu_wind_gpu")
    depends_on("nalu-wind+hypre2~hypre", when="+hypre+amr_wind_gpu~nalu_wind_gpu")
    depends_on("amr-wind+hypre", when="+hypre")
    depends_on("amr-wind~hypre", when="~hypre")
    depends_on("nalu-wind~hypre", when="~hypre")
    depends_on("trilinos+ninja", when="+ninja")
    depends_on("nalu-wind+ninja", when="+ninja")
    depends_on("amr-wind+ninja", when="+ninja")
    depends_on("amr-wind+sycl", when="+amr_wind_gpu+sycl")
    depends_on("nalu-wind@multiphase", when="@multiphase")
    depends_on("amr-wind@multiphase", when="@multiphase")
    # not required but added so these get picked up as a
    # direct dependency when creating snapshots
    depends_on("trilinos")
    depends_on("cmake")
    depends_on("mpi")
    depends_on("nalu-wind+umpire", when="+umpire")
    depends_on("amr-wind+umpire", when="+umpire")
    depends_on("amr-wind+tiny_profile", when="+tiny_profile")
    depends_on("nalu-wind+gpu-aware-mpi", when="+gpu-aware-mpi")
    depends_on("amr-wind+gpu-aware-mpi", when="+gpu-aware-mpi")

    def cmake_args(self):
        spec = self.spec

        args = super(Exawind, self).cmake_args()

        if spec.satisfies("dev_path=*"):
            args.append(self.define("CMAKE_EXPORT_COMPILE_COMMANDS",True))

        args.append(self.define("MPI_HOME", spec["mpi"].prefix))

        if "+umpire" in self.spec:
            args.append(self.define_from_variant("EXAWIND_ENABLE_UMPIRE", "umpire"))
            args.append(self.define("UMPIRE_DIR", self.spec["umpire"].prefix))

        if spec.satisfies("+cuda"):
            args.append(self.define("EXAWIND_ENABLE_CUDA", True))
            args.append(self.define("CUDAToolkit_ROOT", self.spec["cuda"].prefix))
            args.append(self.define("EXAWIND_CUDA_ARCH", self.spec.variants["cuda_arch"].value))

        if spec.satisfies("+rocm"):
            targets = self.spec.variants["amdgpu_target"].value
            args.append(self.define("EXAWIND_ENABLE_ROCM", True))
            args.append("-DCMAKE_CXX_COMPILER={0}".format(self.spec["hip"].hipcc))
            args.append("-DCMAKE_HIP_ARCHITECTURES=" + ";".join(str(x) for x in targets))
            args.append("-DAMDGPU_TARGETS=" + ";".join(str(x) for x in targets))
            args.append("-DGPU_TARGETS=" + ";".join(str(x) for x in targets))

        if spec.satisfies("^amr-wind+hdf5"):
            args.append(self.define("H5Z_ZFP_USE_STATIC_LIBS", True))

        if spec.satisfies("^amr-wind+ascent"):
            # Necessary on Crusher to successfully find OpenMP
            args.append(self.define("CMAKE_EXE_LINKER_FLAGS", self.compiler.openmp_flag))

        return args

    def setup_build_environment(self, env):
        if "~stk_simd" in self.spec:
            env.append_flags("CXXFLAGS", "-DUSE_STK_SIMD_NONE")
        if "+asan" in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}".format(join_path(self.package_dir, "blacklist.asan")))
            env.set("LSAN_OPTIONS", "suppressions={0}".format(join_path(self.package_dir, "sup.asan")))
            env.set("ASAN_OPTIONS", "detect_container_overflow=0")
        if "+rocm+amr_wind_gpu~nalu_wind_gpu" in self.spec:
            # Manually turn off device self.defines to solve Kokkos issues in Nalu-Wind headers
            env.append_flags("CXXFLAGS", "-U__HIP_DEVICE_COMPILE__ -DDESUL_HIP_RDC")
        if "+rocm" in self.spec:
            env.set("OMPI_CXX", self.spec["hip"].hipcc)
            env.set("MPICH_CXX", self.spec["hip"].hipcc)
            env.set("MPICXX_CXX", self.spec["hip"].hipcc)
