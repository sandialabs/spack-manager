from spack import *
from spack.pkg.builtin.tioga import Tioga as bTioga
import os

class Tioga(bTioga):
    depends_on('ninja', type='build')
    generator = 'Ninja'

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(Tioga, self).cmake_args()

        options.append(define('MPI_ROOT', spec['mpi'].prefix))

        if 'dev_path' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        return options


    @run_after('cmake')
    def copy_compile_commands(self):
        if 'dev_path' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
