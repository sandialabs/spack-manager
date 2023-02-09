# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.exawind.exawind import Exawind as bExawind
import spack.config
import os
from shutil import copyfile
import inspect
import re
from spack.util.executable import ProcessError
import manager_cmds.find_machine as fm
from manager_cmds.find_machine import find_machine

class ExawindNightly(bExawind):
    """Extension of exawind for nightly build and test"""

    variant("host_name", default="default")

    phases = ["test", "install"]

    def ctest_args(self):
        spec = self.spec
        options = []
        cmake_options = self.std_cmake_args
        cmake_options += self.cmake_args()
        cmake_options.remove("-G")
        cmake_options.remove("Unix Makefiles") # The space causes problems for ctest

        machine = find_machine(verbose=False)
        full_machine = find_machine(verbose=False, full_machine_name=True)
        if spec.variants["host_name"].value == "default":
            if full_machine == "NOT-FOUND":
                spec.variants["host_name"].value = spec.format("{architecture}")
            else:
                spec.variants["host_name"].value = full_machine

        options.append(self.define("CMAKE_CONFIGURE_ARGS"," ".join(v for v in cmake_options)))
        options.append(self.define("CTEST_SOURCE_DIRECTORY", self.stage.source_path))
        options.append(self.define("CTEST_BINARY_DIRECTORY", self.build_directory))
        options.append(self.define("EXTRA_BUILD_NAME", spec.format("-{compiler}")))
        options.append(self.define("HOST_NAME", spec.variants["host_name"].value))
        options.append(self.define("NP", spack.config.get("config:build_jobs")))
        options.append("-VV")
        options.append("-S")
        options.append(os.path.join(self.stage.source_path,"test","CTestNightlyScript.cmake"))
        return options

    def test(self, spec, prefix):
        """Override base package to run ctest script for nightlies"""
        ctest_args = self.ctest_args()
        with working_dir(self.build_directory, create=True):
            """
            ctest will throw error 255 if there are any warnings
            but that doesn't mean our build failed
            for now just print the error and move on
            """
            inspect.getmodule(self).ctest(*ctest_args, fail_on_error=False)
