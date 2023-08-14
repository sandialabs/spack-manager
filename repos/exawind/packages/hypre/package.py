from spack import *
from spack.pkg.builtin.hypre import Hypre as bHypre
import glob
import os
import shutil
import manager_cmds.find_machine as fm
from manager_cmds.find_machine import find_machine

import spack.util

class Hypre(bHypre):

    phases = ["autoreconf", "distclean", "configure", "clean", "build", "install"]

    variant("gpu-aware-mpi", default=False, description="Use gpu-aware mpi")
    variant("rocblas", default=False, description="use rocblas")
    variant("cublas", default=False, description="use cublas")
    conflicts("+cublas", when="~cuda", msg="cublas requires cuda to be enabled")
    conflicts("+rocblas", when="~rocm", msg="rocblas requires rocm to be enabled")
    variant("umpire", default=False, description="Use Umpire")
    depends_on("umpire", when="+umpire")
    depends_on("umpire+rocm", when="+umpire+rocm")
    depends_on("umpire+cuda", when="+umpire+cuda")
    depends_on("rocprim", when="+rocm")

    def distclean(self, spec, prefix):
        with working_dir("src"):
            if "SPACK_MANAGER_CLEAN_HYPRE" in os.environ:
                make("distclean")

    def clean(self, spec, prefix):
        with working_dir("src"):
            if "SPACK_MANAGER_CLEAN_HYPRE" in os.environ:
                make("clean")

    def do_clean(self):
        super().do_clean()
        if not self.stage.managed_by_spack:
            build_artifacts = glob.glob(os.path.join(self.stage.source_path, "spack-build-*"))
            for f in build_artifacts:
                if os.path.isfile(f):
                    os.remove(f)
                if os.path.isdir(f):
                    shutil.rmtree(f)
            with working_dir(os.path.join(self.stage.source_path, "src")):
                make = spack.util.executable.which("make")
                make("clean")
                make("distclean")

    def flag_handler(self, name, flags):
        if find_machine(verbose=False, full_machine_name=False) == "frontier" and name == "cxxflags" and "+gpu-aware-mpi" in self.spec:
            mpi_include_dir = "-I" + os.path.join(os.getenv("MPICH_DIR"), "include")
            mpi_lib_dir = "-L" + os.path.join(os.getenv("MPICH_DIR"), "lib")
            cray_xpmem_opts = os.path.join(os.getenv("CRAY_XPMEM_POST_LINK_OPTS"), "lib")
            flags.append(mpi_include_dir, mpi_lib_dir, "-lmpi", cray_xpmem_opts, "-lxpmem", os.getenv("PE_MPICH_GTL_DIR_amd_gfx90a"), os.getenv("PE_MPICH_GTL_LIBS_amd_gfx90a"))

        return (flags, None, None)

    def setup_build_environment(self, env):
        spec = self.spec
        if "+mpi" in spec:
            env.set("CC", spec["mpi"].mpicc)
            env.set("CXX", spec["mpi"].mpicxx)
            if "+fortran" in spec:
                env.set("F77", spec["mpi"].mpif77)
            if "+gpu-aware-mpi" in spec and find_machine(verbose=False, full_machine_name=False) == "frontier":
                env.append_flags("HIPFLAGS", "--amdgpu-target=gfx90a")

        if "+cuda" in spec:
            env.set("CUDA_HOME", spec["cuda"].prefix)
            env.set("CUDA_PATH", spec["cuda"].prefix)
            # In CUDA builds hypre currently doesn't handle flags correctly
            env.append_flags("CXXFLAGS", "-O2" if "~debug" in spec else "-g")

        if "+rocm" in spec:
            # As of 2022/04/05, the following are set by 'llvm-amdgpu' and
            # override hypre's default flags, so we unset them.
            env.unset("CFLAGS")
            env.unset("CXXFLAGS")

    def configure_args(self):
        spec = self.spec
        options = super(Hypre, self).configure_args()

        if "+gpu-aware-mpi" in spec:
            options.append("--enable-gpu-aware-mpi")

        if "+rocblas" in spec:
            options.append("--enable-rocblas")

        if "+cublas" in spec:
            options.append("--enable-cublas")

        if "+umpire" in spec:
            if  (("+cuda" in spec or "+rocm" in spec) and "--enable-device-memory-pool" in options):
                options.remove("--enable-device-memory-pool")

        return options
