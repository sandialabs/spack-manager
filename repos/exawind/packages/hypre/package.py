from spack import *
from spack.pkg.builtin.hypre import Hypre as bHypre
import os

class Hypre(bHypre):

    phases = ['autoreconf', 'configure', 'clean', 'build', 'install']

    def clean(self, spec, prefix):
        with working_dir('src'):
            make('clean')

    def _configure_args(self):
        spec = self.spec
        options = super(Hypre, self)._configure_args()                        
                                                                           
        if '+cuda' in self.spec:
            options.append('--enable-cusparse')

        return options
