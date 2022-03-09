from spack import *
from spack.pkg.builtin.hypre import Hypre as bHypre
import os

class Hypre(bHypre):

    def _configure_args(self):
        spec = self.spec
        options = super(Hypre, self)._configure_args()

        return options
