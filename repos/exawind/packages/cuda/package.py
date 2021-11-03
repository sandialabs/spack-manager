import os
from spack import *
from spack.pkg.builtin.cuda import Cuda as bCuda


class Cuda(bCuda):
    def setup_dependent_build_environment(self, env, dependent_spec):
        super(Cuda, self).setup_dependent_build_environment(env, dependent_spec)
        env.append_path('LD_LIBRARY_PATH', os.path.join(self.prefix,'lib64'))
        env.set('CUDA_HOME', self.prefix)

    def setup_run_environment(self, env):
        super(Cuda, self).setup_run_environment(env)
        env.append_path('LD_LIBRARY_PATH', os.path.join(self.prefix,'lib64'))

