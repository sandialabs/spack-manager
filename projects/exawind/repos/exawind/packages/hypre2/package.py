from spack import *
from spack.pkg.builtin.hypre import Hypre as bHypre
import glob
import os
import shutil

class Hypre2(bHypre):

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

    def setup_build_environment(self, env):
        env.set("CFLAGS", self.compiler.cc_pic_flag)

    def configure_args(self):
        spec = self.spec
        options = super(Hypre2, self).configure_args()

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
