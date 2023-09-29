# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.builtin.amr_wind import AmrWind as bAmrWind
import os
from smpackages import *

class AmrWind(SMCMakeExtension, bAmrWind):
    version("multiphase", branch="multiphase_dev", submodules=True)
    
    variant("asan", default=False,
            description="Turn on address sanitizer")
    variant("cppcheck", default=False,
            description="Turn on cppcheck")
    variant("clangtidy", default=False,
            description="Turn on clang-tidy")
    variant("hdf5", default=False,
            description="Enable HDF5 plots with ZFP compression")
    variant("umpire", default=False,
            description="Enable Umpire")
    variant("sycl", default=False,
            description="Enable SYCL backend")
    variant("gpu-aware-mpi", default=False,
            description="gpu-aware-mpi")

    depends_on("hdf5~mpi", when="+hdf5~mpi")
    depends_on("hdf5+mpi", when="+hdf5+mpi")
    depends_on("h5z-zfp", when="+hdf5")
    depends_on("zfp", when="+hdf5")
    depends_on("hypre+umpire", when="+umpire")
    depends_on("hypre+sycl", when="+sycl")
    depends_on("hypre+gpu-aware-mpi", when="+gpu-aware-mpi")

    def setup_build_environment(self, env):
        if "+asan" in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer")
            env.set("LSAN_OPTIONS", "suppressions={0}".format(join_path(self.package_dir, "sup.asan")))
        if "%intel" in self.spec:
            env.append_flags("CXXFLAGS", "-no-ipo")

    def cmake_args(self):
        spec = self.spec
        cmake_options = super(AmrWind, self).cmake_args()

        if "+cppcheck" in spec:
            cmake_options.append(self.define("AMR_WIND_ENABLE_CPPCHECK", True))

        if "+clangtidy" in spec:
            cmake_options.append(self.define("AMR_WIND_ENABLE_CLANG_TIDY", True))

        if spec.satisfies("dev_path=*"):
            cmake_options.append(self.define("CMAKE_EXPORT_COMPILE_COMMANDS", True))

        if "+umpire" in self.spec:
            cmake_options.append(self.define_from_variant("AMR_WIND_ENABLE_UMPIRE", "umpire"))
            cmake_options.append(self.define("UMPIRE_DIR", self.spec["umpire"].prefix))

        if "+cuda" in self.spec:
            targets = self.spec.variants["cuda_arch"].value
            cmake_options.append("-DCMAKE_CUDA_ARCHITECTURES=" + ";".join(str(x) for x in targets))

        if "+hdf5" in spec:
            cmake_options.append(self.define("AMR_WIND_ENABLE_HDF5", True))
            cmake_options.append(self.define("AMR_WIND_ENABLE_HDF5_ZFP", True))
            # Help AMReX understand if HDF5 is parallel or not.
            # Building HDF5 with CMake as Spack does, causes this inspection to break.
            if "+mpi" in spec:
                cmake_options.append(self.define("HDF5_IS_PARALLEL", True))
            else:
                cmake_options.append(self.define("HDF5_IS_PARALLEL", False))

        if "+rocm" in self.spec:
            # Used as an optimization to only list the single specified
            # arch in the offload-arch compile line, but not explicitly necessary
            targets = self.spec.variants["amdgpu_target"].value
            cmake_options.append("-DCMAKE_HIP_ARCHITECTURES=" + ";".join(str(x) for x in targets))
            cmake_options.append("-DAMDGPU_TARGETS=" + ";".join(str(x) for x in targets))
            cmake_options.append("-DGPU_TARGETS=" + ";".join(str(x) for x in targets))

        if "+sycl" in self.spec:
            cmake_options.append(self.define("AMR_WIND_ENABLE_SYCL", True))
            # SYCL GPU backend only supported with Intel's oneAPI or DPC++ compilers
            sycl_compatible_compilers = ["dpcpp", "icpx"]
            if not (os.path.basename(self.compiler.cxx) in sycl_compatible_compilers):
                raise InstallError(
                    "AMReX's SYCL GPU Backend requires DPC++ (dpcpp)"
                    + " or the oneAPI CXX (icpx) compiler."
                )

        if "+tests" in spec:
            spack_manager_local_golds = os.path.join(os.getenv("SPACK_MANAGER"), "golds")
            spack_manager_golds_dir = os.getenv("SPACK_MANAGER_GOLDS_DIR", default=spack_manager_local_golds)
            saved_golds = os.path.join(spack_manager_golds_dir, "tmp", "amr-wind")
            current_golds = os.path.join(spack_manager_golds_dir, "current", "amr-wind")
            os.makedirs(saved_golds, exist_ok=True)
            os.makedirs(current_golds, exist_ok=True)
            cmake_options.append(self.define("AMR_WIND_TEST_WITH_FCOMPARE", True))
            cmake_options.append(self.define("AMR_WIND_SAVE_GOLDS", True))
            cmake_options.append(self.define("AMR_WIND_SAVED_GOLDS_DIRECTORY", saved_golds))
            cmake_options.append(self.define("AMR_WIND_REFERENCE_GOLDS_DIRECTORY", current_golds))

        return cmake_options
