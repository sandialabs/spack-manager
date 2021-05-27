from spack import *
from spack.pkg.exawind.nalu_wind_developer import NaluWindDeveloper as bNaluWind
import spack.config
import os
from shutil import copyfile
import inspect
import re
from spack.util.executable import ProcessError

def variant_peeler(var_str):
    """strip out everything but + variants and build types"""
    output = ''
    # extract all the + variants
    for match in re.finditer(r'(?<=\+)([a-z0-9]*)', var_str):
        output+='+{v}'.format(v=var_str[match.start(): match.end()])
    # extract build type
    for match in re.finditer('r(?<=build_type=)(a-zA-Z)', var_str):
        output = var_str[match.start():match.end()] + ' ' + output
    return output


class NaluWindNightly(bNaluWind, CudaPackage):
    """Extension of Nalu-Wind for nightly build and test"""
    maintainers = ['psakievich']

    variant('host_name', default='default')
    variant('extra_name', default='default')
    #variant('NP', default=1)
    generator = 'Unix Makefiles'
    version('master', branch='master', submodules=True)

    def ctest_args(self):
        spec = self.spec
        define = CMakePackage.define
        if spec.variants['host_name'].value == 'default':
            spec.variants['host_name'].value = spec.format('{architecture}')
        if spec.variants['extra_name'].value == 'default':
            extra_name = spec.format(' {compiler} ')
            var =  spec.format('{variants}')
            temp =  variant_peeler(var)
            extra_name = extra_name + temp
            spec.variants['extra_name'].value = extra_name
        options = []
        options.extend([define('TESTING_ROOT_DIR', self.stage.path),
            define('NALU_DIR', self.stage.source_path),
            define('TEST_LOG', os.path.join(self.build_directory, 'nalu-wind-test-log.txt')),
            define('BUILD_DIR', self.build_directory)])
        cmake_options = self.std_cmake_args
        cmake_options += self.cmake_args()
        options.append(define('CMAKE_CONFIGURE_ARGS=',' '.join(v for v in cmake_options)))
        options.append(define('HOST_NAME', spec.variants['host_name'].value))
        options.append(define('EXTRA_BUILD_NAME', spec.variants['extra_name'].value))
        # Pass num procs spack is using into the build script
        options.append(define('NP', spack.config.get('config:build_jobs')))
        #options.append(define('NP', spec.variants['NP'].value))
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
            """
            ctest will throw error 255 if there are any warnings
            but that doesn't mean our build failed
            for now just print the error and move on
            """
            inspect.getmodule(self).ctest(*ctest_args, fail_on_error=False)
