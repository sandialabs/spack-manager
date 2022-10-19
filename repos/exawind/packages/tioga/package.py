# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.builtin.tioga import Tioga as bTioga
import os

class Tioga(bTioga):
    git = "https://github.com/Exawind/tioga.git"

    variant('asan', default=False,
            description='turn on address sanitizer')

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(Tioga, self).cmake_args()

        if 'dev_path' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        return options

    def setup_build_environment(self, env):
        if '+asan' in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}".format(join_path(self.package_dir, 'sup.asan')))

    @run_after('cmake')
    def copy_compile_commands(self):
        if 'dev_path' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
