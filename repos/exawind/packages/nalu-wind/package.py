# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.builtin.nalu_wind import NaluWind as bNaluWind
from spack.pkg.builtin.kokkos import Kokkos
import os
from shutil import copyfile

class NaluWind(bNaluWind, ROCmPackage):
    version('master', branch='master', submodules=True)

    variant('asan', default=False,
            description='Turn on address sanitizer')
    variant('stk_simd', default=False,
            description='Enable SIMD in STK')

    depends_on('hypre+unified-memory', when='+hypre+cuda')
    depends_on('trilinos gotype=long')

    for _arch in ROCmPackage.amdgpu_targets:
        depends_on('trilinos@master: ~shared+exodus+tpetra+muelu+belos+ifpack2+amesos2+zoltan+stk+boost~superlu-dist~superlu+hdf5+shards~hypre+gtest+rocm~rocm_rdc amdgpu_target={0}'.format(_arch),
                   when='+rocm amdgpu_target={0}'.format(_arch))

    cxxstd=['14', '17']
    variant('cxxstd', default='14', values=cxxstd,  multi=False)
    variant('tests', default=True, description='Activate regression tests')

    for std in cxxstd:
        depends_on('trilinos cxxstd=%s' % std, when='cxxstd=%s' % std)

    def setup_build_environment(self, env):
        if '~stk_simd' in self.spec:
            env.append_flags('CXXFLAGS', '-DUSE_STK_SIMD_NONE')
        if '+asan' in self.spec:
            env.append_flags('CXXFLAGS', '-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}'.format(join_path(self.package_dir, 'blacklist.asan')))
            env.set("LSAN_OPTIONS", "suppressions={0}".format(join_path(self.package_dir, 'sup.asan')))
            env.set("ASAN_OPTIONS", "detect_container_overflow=0")
        if '+cuda' in self.spec:
            env.set("CUDA_LAUNCH_BLOCKING", "1")
            env.set("CUDA_MANAGED_FORCE_DEVICE_ALLOC", "1")
            env.set('OMPI_CXX', self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set('MPICH_CXX', self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set('MPICXX_CXX', self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        cmake_options = super(NaluWind, self).cmake_args()
        cmake_options.append(self.define_from_variant('CMAKE_CXX_STANDARD', 'cxxstd'))

        if  spec.satisfies('dev_path=*'):
            cmake_options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))
            cmake_options.append(define('ENABLE_TESTS', True))

        if '+rocm' in self.spec:
            cmake_options.append('-DCMAKE_CXX_COMPILER={0}'.format(self.spec['hip'].hipcc))
            cmake_options.append(define('ENABLE_ROCM', True))

        if spec['mpi'].name == 'openmpi':
            cmake_options.append(define('MPIEXEC_PREFLAGS','--oversubscribe'))

        if spec.satisfies('+tests') or self.run_tests or spec.satisfies('dev_path=*'):
            saved_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'golds', 'tmp', 'nalu-wind')
            current_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'golds', 'current', 'nalu-wind')
            os.makedirs(saved_golds, exist_ok=True)
            os.makedirs(current_golds, exist_ok=True)
            cmake_options.append(define('NALU_WIND_SAVE_GOLDS', True))
            cmake_options.append(define('NALU_WIND_SAVED_GOLDS_DIR', saved_golds))
            cmake_options.append(define('NALU_WIND_REFERENCE_GOLDS_DIR', current_golds))

        return cmake_options

    @run_after('cmake')
    def copy_compile_commands(self):
        if self.spec.satisfies('dev_path=*'):
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
