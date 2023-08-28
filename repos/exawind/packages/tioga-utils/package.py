# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
import os
from smpackages import *

class TiogaUtils(SMCMakeExtension):
    git = "https://github.com/Exawind/tioga_utils.git"

    version("exawind", branch="exawind")

    depends_on("trilinos")
    depends_on("yaml-cpp")
    depends_on("tioga~nodegid")
    depends_on("nalu-wind")
 
    def cmake_args(self):
        spec = self.spec
        options = super(TiogaUtils, self).cmake_args()

        if spec.satisfies("dev_path=*"):
            options.append(self.define("CMAKE_EXPORT_COMPILE_COMMANDS",True))

        return options

