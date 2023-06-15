# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *


class HypreMiniApp(CMakePackage, CudaPackage, ROCmPackage):
    """HYPRE mini-app for use with Nalu-Wind linear systems. """

    homepage = "https://github.com/Exawind/hypre-mini-app"
    git      = "https://github.com/Exawind/hypre-mini-app.git"

    maintainers = ["jrood-nrel"]

    tags = ["ecp", "ecp-apps"]

    version("master", branch="master", submodules=True)

    variant("umpire", default=False,
            description="Enable Umpire")

    variant("unified-memory", default=False,
            description="Enable Unified Memory in hypre")

    variant("gpu-aware-mpi", default=False,
            description="gpu-aware-mpi")

    variant("rocblas", default=False,
            description="use rocblas")

    variant("cublas", default=False,
            description="use cublas")

    depends_on("mpi")
    depends_on("hypre+mpi@2.20.0:")
    depends_on("yaml-cpp@0.6.2:")
    depends_on("hypre+umpire", when="+umpire")
    depends_on("hypre+unified-memory", when="+unified-memory")
    depends_on("hypre+gpu-aware-mpi", when="+gpu-aware-mpi")
    depends_on("hypre+rocblas", when="+rocblas")
    depends_on("hypre+cublas", when="+cublas")
    for arch in CudaPackage.cuda_arch_values:
        depends_on("hypre+cuda cuda_arch=%s @2.20.0:" % arch,
                   when="+cuda cuda_arch=%s" % arch)
    for arch in ROCmPackage.amdgpu_targets:
        depends_on("hypre+rocm amdgpu_target=%s" % arch,
                   when="+rocm amdgpu_target=%s" % arch)

    def cmake_args(self):
        args = [
            self.define("HYPRE_DIR", self.spec["hypre"].prefix),
            self.define("YAML_ROOT_DIR", self.spec["yaml-cpp"].prefix),
            self.define_from_variant("ENABLE_CUDA", "cuda"),
            self.define_from_variant("ENABLE_HIP", "rocm"),
        ]

        args.append(self.define_from_variant("ENABLE_UMPIRE", "umpire"))
        if "+umpire" in self.spec:
            args.append(self.define("UMPIRE_DIR", self.spec["umpire"].prefix))

        if "+rocm" in self.spec:
            args.append(self.define("CMAKE_CXX_COMPILER", self.spec["hip"].hipcc))

        return args
