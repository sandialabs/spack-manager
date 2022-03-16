from spack import *
from spack.pkg.builtin.hypre import Hypre as bHypre
import os

class Hypre(bHypre):

    phases = ['autoreconf', 'distclean', 'configure', 'clean', 'build', 'install']

    def distclean(self, spec, prefix):
        with working_dir('src'):
            if 'SPACK_MANAGER_CLEAN_HYPRE' in os.environ:
                make('distclean')

    def clean(self, spec, prefix):
        with working_dir('src'):
            if os.environ.get('SPACK_MANAGER_CLEAN_HYPRE') is not None:
                make('clean')

    def _configure_args(self):
        spec = self.spec
        options = super(Hypre, self)._configure_args()

        return options
