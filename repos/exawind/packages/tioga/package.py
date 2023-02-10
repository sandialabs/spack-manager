# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.builtin.tioga import Tioga as bTioga
import os
from smpackages import *

class Tioga(bTioga, SMCMakeExtension):
    git = "https://github.com/Exawind/tioga.git"

    variant("asan", default=False,
            description="turn on address sanitizer")

    def cmake_args(self):
        spec = self.spec
        options = super(Tioga, self).cmake_args()

        if spec.satisfies("dev_path=*"):
            options.append(self.define("CMAKE_EXPORT_COMPILE_COMMANDS",True))

        return options

    def setup_build_environment(self, env):
        if "+asan" in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}".format(join_path(self.package_dir, "sup.asan")))
