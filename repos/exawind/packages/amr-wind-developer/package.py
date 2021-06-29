from spack import *
from spack.pkg.exawind.amr_wind import AmrWind as bAmrWind
#from spack.pkg.builtin.amr_wind import AmrWind as bAmrWind
import os
from shutil import copyfile

class AmrWindDeveloper(bAmrWind):
    variant('compile_commands', default=False,
            description='generate compile_commands.json and copy to source dir')

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(AmrWindDeveloper, self).cmake_args()

        options.append(define('AMR_WIND_SAVE_GOLDS', True))
        options.append(define('AMR_WIND_SAVED_GOLDS_DIRECTORY', os.path.join(os.getenv('SPACK_MANAGER'), 'tmp', 'tmp_golds')))

        if spec['mpi'].name == 'openmpi':
            options.append(define('MPIEXEC_PREFLAGS', '--oversubscribe'))

        if '+compile_commands' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        if '+compile_commands' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
