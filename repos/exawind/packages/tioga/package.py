# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.builtin.tioga import Tioga as bTioga
import os
import sys

class Tioga(bTioga):

    patch('iargc.patch')

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
