from spack.pkg.builtin.hypre import Hypre as bHypre

class Hypre(bHypre):
    variant('shared', default=True, description="Build shared library (disables static library)")
