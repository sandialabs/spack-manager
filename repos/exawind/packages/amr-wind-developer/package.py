from spack import *
from spack.pkg.pending.amr_wind import AmrWind as bAmrWind
import os
from shutil import copyfile

class AmrWindDeveloper(bAmrWind):
    variant('compile_commands', default=False,
            description='generate compile_commands.json and copy to source dir')

    depends_on('ninja', type='build')
    generator = 'Ninja'

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(AmrWindDeveloper, self).cmake_args()

        if spec['mpi'].name == 'openmpi':
            options.append(define('MPIEXEC_PREFLAGS', '--oversubscribe'))

        if '+compile_commands' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        saved_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'tmp', 'tmp_golds', 'amr-wind')
        current_golds = os.path.join(os.getenv('SPACK_MANAGER'), 'golds', 'current', 'amr-wind')
        linked_golds = os.path.join(self.stage.source_path, "test", "AMR-WindGoldFiles")
        options.append(define('AMR_WIND_SAVE_GOLDS', True))
        options.append(define('AMR_WIND_SAVED_GOLDS_DIRECTORY', saved_golds))
        if not os.path.lexists(linked_golds):
            os.symlink(current_golds, linked_golds)

        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        if '+compile_commands' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
