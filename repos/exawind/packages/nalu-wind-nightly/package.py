from spack import *
from spack.pkg.exawind.nalu_wind import NaluWind as bNaluWind
import os
from shutil import copyfile
import inspect

class NaluWindNightly(bNaluWind, CudaPackage):
    """Extension of Nalu-Wind for nightly build and test"""
    maintaniers = ['psakievich']
    git = 'https://github.com/psakievich/nalu-wind.git'

    variant('host_name', default='default')
    variant('extra_name', default='default')
    generator = 'Unix Makefiles'
    version('nightly', branch='cdash', submodules=True)

    def ctest_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = []
        if self.stage.path is None:
            print("ERROR ERROR ERROR")
            exit()
        options.extend([define('TESTING_ROOT_DIR', self.stage.path),
            define('NALU_DIR', self.stage.source_path),
            define('TEST_LOG', os.path.join(self.build_directory, 'nalu-wind-test-log.txt')),
            define('BUILD_DIR', self.build_directory)])
        cmake_options = self.cmake_args()
        options.append(define('CMAKE_CONFIGURE_ARGS=',' '.join(v for v in cmake_options)))
        options.append(define('HOST_NAME', spec.variants['host_name'].value))
        options.append(define('EXTRA_BUILD_NAME', spec.variants['extra_name'].value))
        options.append('-VV')
        options.append('-S')
        options.append(os.path.join(self.stage.source_path,'reg_tests','CTestNightlyScript.cmake'))

        return options

    def check(self):
        return
    def cmake(self, spec, prefix):
        return
#    def install(self, spec, prefix):
#        return

    def build(self, spec, prefix):
        """override base package to run ctest script for nightlies"""
        ctest_args = self.ctest_args()
        with working_dir(self.build_directory, create=True):
            inspect.getmodule(self).ctest(*ctest_args)
