from spack import *
from spack.pkg.builtin.amr_wind import AmrWind as bAmrWind
import os
from shutil import copyfile

class AmrWind(bAmrWind):
    depends_on('ninja', type='build')
    generator = 'Ninja'

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(AmrWind, self).cmake_args()

        if '+cuda' in spec:
            options.append(define('BUILD_SHARED_LIBS', False))

        if spec['mpi'].name == 'openmpi':
            options.append(define('MPIEXEC_PREFLAGS', '--oversubscribe'))

        if spec.satisfies('dev_path=*'):
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if '+mpi' in spec:
            options.append(define('MPI_ROOT', spec['mpi'].prefix))

        saved_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'tmp', 'tmp_golds', 'amr-wind')
        current_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'golds', 'current', 'amr-wind')
        linked_golds = os.path.join(self.stage.source_path, "test", "AMR-WindGoldFiles")
        # Make this a variant in the future
        options.append(define('AMR_WIND_SAVE_GOLDS', False))
        options.append(define('AMR_WIND_SAVED_GOLDS_DIRECTORY', saved_golds))
        if not os.path.lexists(linked_golds):
            os.symlink(current_golds, linked_golds)

        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        if self.spec.satisfies('dev_path=*'):
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
