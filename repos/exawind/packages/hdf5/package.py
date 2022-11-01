# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack.pkg.builtin.hdf5 import Hdf5 as bHdf5
import os

class Hdf5(bHdf5):
    @run_after("install")
    def symlink_to_h5hl_wrappers(self):
        if self.spec.satisfies("@1.8.21:1.8.22,1.10.2:1.10.7,1.12.0+hl"):
            with working_dir(self.prefix.bin):
                # CMake's FindHDF5 relies only on h5cc so it doesn't find the HL component unless it uses h5hlcc
                # so we symlink h5cc to h5hlcc etc
                os.remove("h5cc")
                os.remove("h5c++")
                symlink("h5hlcc", "h5cc")
                symlink("h5hlc++", "h5c++")
