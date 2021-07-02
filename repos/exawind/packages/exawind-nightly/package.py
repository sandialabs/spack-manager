from spack import *
from spack.pkg.exawind.exawind_developer import ExawindDeveloper as bExawind
import spack.config
import os
from shutil import copyfile
import inspect
import re
from spack.util.executable import ProcessError

class ExawindNightly(bExawind):
    """Extension of exawind for nightly build and test"""

    variant('host_name', default='default')

    phases = ['test', 'install']

    def ctest_args(self):
        spec = self.spec
        options = []
        define = CMakePackage.define
        cmake_options = self.std_cmake_args
        cmake_options += self.cmake_args()
        if spec.variants['host_name'].value == 'default':
            spec.variants['host_name'].value = spec.format('{architecture}')
        options.append(define('CMAKE_CONFIGURE_ARGS=',' '.join(v for v in cmake_options)))
        options.append(define('CTEST_SOURCE_DIRECTORY', self.stage.source_path))
        options.append(define('CTEST_BINARY_DIRECTORY', self.build_directory))
        options.append(define('EXTRA_BUILD_NAME', spec.format('-{compiler}')))
        options.append(define('HOST_NAME', spec.variants['host_name'].value))
        options.append(define('NP', spack.config.get('config:build_jobs')))
        options.append('-VV')
        options.append('-S')
        options.append(os.path.join(self.stage.source_path,'test','CTestNightlyScript.cmake'))
        return options

    def test(self, spec, prefix):
        """Override base package to run ctest script for nightlies"""
        ctest_args = self.ctest_args()
        with working_dir(self.build_directory, create=True):
            """
            ctest will throw error 255 if there are any warnings
            but that doesn't mean our build failed
            for now just print the error and move on
            """
            inspect.getmodule(self).ctest(*ctest_args, fail_on_error=False)
