from spack import *
from spack.pkg.builtin.tioga import Tioga as bTioga
import os
import sys

class Tioga(bTioga):

    patch('iargc_cce.patch', when='%cce@12:')

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(Tioga, self).cmake_args()

        options.append(define('MPI_ROOT', spec['mpi'].prefix))

        # On some systems these are necessary, on some systems it causes failures
        if sys.platform == 'darwin':
            options.append(self.define('CMAKE_CXX_COMPILER', spec['mpi'].mpicxx))
            options.append(self.define('CMAKE_C_COMPILER', spec['mpi'].mpicc))
            options.append(self.define('CMAKE_Fortran_COMPILER', spec['mpi'].mpifc))

        if 'dev_path' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        return options


    @run_after('cmake')
    def copy_compile_commands(self):
        if 'dev_path' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
