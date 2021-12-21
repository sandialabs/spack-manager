from spack import *
from spack.pkg.builtin.amr_wind import AmrWind as bAmrWind
import os
from shutil import copyfile

class AmrWind(bAmrWind, ROCmPackage):

    depends_on('hypre+unified-memory', when='+hypre+cuda')
    depends_on('py-matplotlib', when='+masa')
    depends_on('py-pandas', when='+masa')

    variant('asan', default=False,
            description='Turn on address sanitizer')

    def setup_build_environment(self, env):
        if '+asan' in self.spec:
            env.append_flags('CXXFLAGS', '-fsanitize=address -fno-omit-frame-pointer')
            env.set("LSAN_OPTIONS", "suppressions={0}".format(join_path(self.package_dir, 'sup.asan')))
        if '%intel' in self.spec:
            env.append_flags('CXXFLAGS', '-no-ipo')

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(AmrWind, self).cmake_args()

        if '+cuda' in spec:
            options.append(define('BUILD_SHARED_LIBS', False))

        if '+rocm' in self.spec:
            targets = self.spec.variants['amdgpu_target'].value
            options.append('-DCMAKE_CXX_COMPILER={0}'.format(self.spec['hip'].hipcc))
            options.append('-DAMR_WIND_ENABLE_ROCM=ON')
            options.append('-DAMReX_AMD_ARCH=' + ';'.join(str(x) for x in targets))

        if spec['mpi'].name == 'openmpi':
            options.append(define('MPIEXEC_PREFLAGS', '--oversubscribe'))

        if spec.satisfies('dev_path=*'):
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if '+mpi' in spec:
            options.append(define('MPI_ROOT', spec['mpi'].prefix))

        if '+tests' in spec:
            # Make directories a variant in the future
            saved_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'golds', 'tmp', 'amr-wind')
            current_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'golds', 'current', 'amr-wind')
            os.makedirs(saved_golds, exist_ok=True)
            os.makedirs(current_golds, exist_ok=True)
            options.append(define('AMR_WIND_SAVE_GOLDS', True))
            options.append(define('AMR_WIND_SAVED_GOLDS_DIRECTORY', saved_golds))
            options.append(define('AMR_WIND_REFERENCE_GOLDS_DIRECTORY', current_golds))

        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        if self.spec.satisfies('dev_path=*'):
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
