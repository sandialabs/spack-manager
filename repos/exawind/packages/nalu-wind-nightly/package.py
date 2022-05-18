# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.exawind.nalu_wind import NaluWind as bNaluWind
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
        output = var_str[match.start():match.end()] + output
    return output


class NaluWindNightly(bNaluWind, CudaPackage):
    """Extension of Nalu-Wind for nightly build and test"""
    maintainers = ['psakievich']

    version('master', branch='master', submodules=True)

    variant('host_name', default='default')
    variant('extra_name', default='default')

    variant('snl', default=False, description='Reports to SNL dashboard')
    patch('snl_ctest.patch', when='+snl')

    phases = ['test']

    def dashboard_build_name(self):
        variants = '-' + self.dashboard_variants() if '+snl' in self.spec else ''
        return '-{}{}^{}'.format(self.dashboard_compilers(), variants, self.dashboard_trilinos())

    def dashboard_compilers(self):
        compilers = self.spec.format('{compiler}')
        if 'cuda' in self.spec:
            compilers = '{}-cuda@{}'.format(compilers, self.spec['cuda'].version)
        return compilers

    def dashboard_trilinos(self):
        trilinos = 'trilinos@{}'.format(self.spec['trilinos'].version)
        if 'cuda' in self.spec:
            trilinos = '{}{}'.format(trilinos, self.spec['trilinos'].format('{variants.uvm}'))
        return trilinos

    def dashboard_variants(self):
        blacklist = ['build_type', 'snl', 'pic', 'cuda', 'cuda_arch', 'tests']
        printable = [v for v in self.spec.variants if v not in blacklist]
        enabled = [v for v in printable if self.spec.variants[v].value]

        build_type = self.spec.format('{variants.build_type}').split('=')[1]
        formatted = ''.join([self.spec.format('{variants.' + variant + '}') for variant in enabled])
        return build_type + formatted

    def ctest_args(self):
        spec = self.spec
        define = CMakePackage.define
        machine = find_machine(verbose=False, full_machine_name=True)

        if spec.variants['host_name'].value == 'default':
            if machine == 'NOT-FOUND':
                spec.variants['host_name'].value = spec.format('{architecture}')
            else:
                spec.variants['host_name'].value = machine

        if spec.variants['extra_name'].value == 'default':
            compilers = spec.format('{compiler}')
            trilinos = 'trilinos@' + str(spec['trilinos'].version)

            if '+cuda' in spec:
                compilers += '-cuda@' + str(spec['cuda'].version)
                if '+uvm' in spec['trilinos']:
                    trilinos = trilinos + '+uvm'
                else:
                    trilinos = trilinos + '~uvm'

            extra_name = '-' + compilers
            if '+snl' in spec:
                variants = variant_peeler(spec.format('{variants}'))
                extra_name = extra_name + '-' + variants
            extra_name = extra_name + '^' + trilinos
            spec.variants['extra_name'].value = extra_name

        # Cmake options for ctest
        cmake_options = self.std_cmake_args
        cmake_options += self.cmake_args()
        cmake_options.remove('-G')
        cmake_options.remove('Unix Makefiles') # The space causes problems for ctest
        if '%intel' in spec and '-DBoost_NO_BOOST_CMAKE=ON' in cmake_options:
            cmake_options.remove('-DBoost_NO_BOOST_CMAKE=ON') # Avoid dashboard warning
        if machine == 'eagle.hpc.nrel.gov':
            cmake_options.append(define('TEST_ABS_TOL', '1e-10'))
            cmake_options.append(define('TEST_REL_TOL', '1e-8'))

        # Ctest options
        ctest_options = []
        ctest_options.extend([define('TESTING_ROOT_DIR', self.stage.path),
            define('NALU_DIR', self.stage.source_path),
            define('BUILD_DIR', self.build_directory)])
        if machine == 'eagle.hpc.nrel.gov':
            ctest_options.append(define('CTEST_DISABLE_OVERLAPPING_TESTS', True))
            ctest_options.append(define('UNSET_TMPDIR_VAR', True))
        ctest_options.append(define('CMAKE_CONFIGURE_ARGS',' '.join(v for v in cmake_options)))
        ctest_options.append(define('HOST_NAME', spec.variants['host_name'].value))
        ctest_options.append(define('EXTRA_BUILD_NAME', spec.variants['extra_name'].value))
        ctest_options.append(define('NP', spack.config.get('config:build_jobs')))
        ctest_options.append('-VV')
        ctest_options.append('-S')
        ctest_options.append(os.path.join(self.stage.source_path,'reg_tests','CTestNightlyScript.cmake'))

        return ctest_options

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
