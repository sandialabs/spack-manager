from spack import *
from spack.pkg.builtin.amr_wind import AmrWind as bAmrWind
import os
from shutil import copyfile

class AmrWind(bAmrWind, ROCmPackage):

    depends_on('hypre2+unified-memory', when='+hypre+cuda')
    depends_on('py-matplotlib', when='+masa')
    depends_on('py-pandas', when='+masa')

    for _arch in ROCmPackage.amdgpu_targets:
        depends_on('hypre2~int64+rocm amdgpu_target={0}'.format(_arch), when='+hypre+rocm amdgpu_target={0}'.format(_arch))

    variant('asan', default=False,
            description='Turn on address sanitizer')
    variant('cppcheck', default=False,
            description='Turn on cppcheck')
    variant('clangtidy', default=False,
            description='Turn on clang-tidy')

    def setup_build_environment(self, env):
        if '+asan' in self.spec:
            env.append_flags('CXXFLAGS', '-fsanitize=address -fno-omit-frame-pointer')
            env.set("LSAN_OPTIONS", "suppressions={0}".format(join_path(self.package_dir, 'sup.asan')))
        if '%intel' in self.spec:
            env.append_flags('CXXFLAGS', '-no-ipo')

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        cmake_options = super(AmrWind, self).cmake_args()

        if '+cppcheck' in spec:
            cmake_options.append(define('AMR_WIND_ENABLE_CPPCHECK', True))

        if '+clangtidy' in spec:
            cmake_options.append(define('AMR_WIND_ENABLE_CLANG_TIDY', True))

        if '+cuda' in spec:
            cmake_options.append(define('BUILD_SHARED_LIBS', False))

        if '+rocm' in self.spec:
            targets = self.spec.variants['amdgpu_target'].value
            cmake_options.append('-DCMAKE_CXX_COMPILER={0}'.format(self.spec['hip'].hipcc))
            cmake_options.append(define('AMR_WIND_ENABLE_ROCM', True))
            cmake_options.append('-DAMReX_AMD_ARCH=' + ';'.join(str(x) for x in targets))
            cmake_options.append('-DCMAKE_HIP_ARCHITECTURES=' + ';'.join(str(x) for x in targets))
            cmake_options.append('-DAMDGPU_TARGETS=' + ';'.join(str(x) for x in targets))
            cmake_options.append('-DGPU_TARGETS=' + ';'.join(str(x) for x in targets))

        if spec['mpi'].name == 'openmpi':
            cmake_options.append(define('MPIEXEC_PREFLAGS', '--oversubscribe'))

        if spec.satisfies('dev_path=*'):
            cmake_options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if '+mpi' in spec:
            cmake_options.append(define('MPI_ROOT', spec['mpi'].prefix))

        if '+tests' in spec:
            saved_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'golds', 'tmp', 'amr-wind')
            current_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'golds', 'current', 'amr-wind')
            os.makedirs(saved_golds, exist_ok=True)
            os.makedirs(current_golds, exist_ok=True)
            cmake_options.append(define('AMR_WIND_SAVE_GOLDS', True))
            cmake_options.append(define('AMR_WIND_SAVED_GOLDS_DIRECTORY', saved_golds))
            cmake_options.append(define('AMR_WIND_REFERENCE_GOLDS_DIRECTORY', current_golds))

        return cmake_options

    @run_after('cmake')
    def copy_compile_commands(self):
        if self.spec.satisfies('dev_path=*'):
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
