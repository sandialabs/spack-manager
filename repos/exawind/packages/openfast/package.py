# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack.pkg.builtin.openfast import Openfast as bOpenfast

class Openfast(bOpenfast):
    # Avoid using HDF5's installed CMake config with hdf5-shared library names
    def cmake_args(self):
        options = super(Openfast, self).cmake_args()
        options.append('-DHDF5_NO_FIND_PACKAGE_CONFIG_FILE:BOOL=ON')
        return options
