from spack import *
from spack.pkg.exawind.amr_wind import AmrWind as bAmrWind
import spack.config
import os
from shutil import copyfile
import inspect
import re
from spack.util.executable import ProcessError
import manager_cmds.find_machine as fm
from manager_cmds.find_machine import find_machine

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

class AmrWindNightly(bAmrWind):
    """Extension of amr-wind for nightly build and test"""

    variant('host_name', default='default')
    variant('extra_name', default='default')
    variant('latest_amrex', default=False)

    phases = ['test']

    def ctest_args(self):
        spec = self.spec
        define = CMakePackage.define
        if spec.variants['host_name'].value == 'default':
            machine = find_machine(verbose=False, full_machine_name=True)
            if machine == 'NOT-FOUND':
                spec.variants['host_name'].value = spec.format('{architecture}')
            else:
                spec.variants['host_name'].value = machine
        if spec.variants['extra_name'].value == 'default':
            spec.variants['extra_name'].value = spec.format('-{compiler}')
            if '+cuda' in spec:
                spec.variants['extra_name'].value = spec.variants['extra_name'].value + '-cuda@' + str(spec['cuda'].version)
            if spec.variants['latest_amrex'].value == True:
                spec.variants['extra_name'].value = spec.variants['extra_name'].value + '-latest-amrex'
        options = []
        options.extend([define('TESTING_ROOT_DIR', self.stage.path),
            define('SOURCE_DIR', self.stage.source_path),
            define('BUILD_DIR', self.build_directory)])
        cmake_options = self.std_cmake_args
        cmake_options += self.cmake_args()
        cmake_options.remove('-G')
        cmake_options.remove('Unix Makefiles') # The space causes problems for ctest
        options.append(define('CMAKE_CONFIGURE_ARGS',' '.join(v for v in cmake_options)))
        options.append(define('HOST_NAME', spec.variants['host_name'].value))
        options.append(define('EXTRA_BUILD_NAME', spec.variants['extra_name'].value))
        options.append(define('USE_LATEST_AMREX', spec.variants['latest_amrex'].value))
        options.append(define('NP', spack.config.get('config:build_jobs')))
        options.append('-VV')
        options.append('-S')
        options.append(os.path.join(self.stage.source_path,'test','CTestNightlyScript.cmake'))
        return options

    def test(self, spec, prefix):
        """override base package to run ctest script for nightlies"""
        ctest_args = self.ctest_args()
        with working_dir(self.build_directory, create=True):
            """
            ctest will throw error 255 if there are any warnings
            but that doesn't mean our build failed
            for now just print the error and move on
            """
            inspect.getmodule(self).ctest(*ctest_args, fail_on_error=False)
