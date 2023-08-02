# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack.pkg.builtin.openfast import Openfast as bOpenfast
import manager_cmds.find_machine as fm
from manager_cmds.find_machine import find_machine

class Openfast(bOpenfast):
    patch("hub_seg_fault.patch", when="@2.7:3.2")
    patch("segfault_message.patch", when="%clang@12.0.1 build_type=RelWithDebInfo")
    version("fsi", git="https://github.com/gantech/openfast.git", branch="f/br_fsi_2")

    variant("rosco", default=False,
            description="Build ROSCO controller alongside OpenFAST")

    depends_on("rosco", when="+rosco")
    depends_on("netcdf-c", when="@fsi")

    #def setup_build_environment(self, env):
    #    spec = self.spec
    #    machine = find_machine(verbose=False, full_machine_name=False)
    #    if machine == "crusher" or machine == "frontier":
    #        env.unset("SPACK_TARGET_ARGS")
