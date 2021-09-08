from spack.pkg.builtin.openfast import Openfast as bOpenfast

class Openfast(bOpenfast):
    # Avoid using HDF5's installed CMake config with hdf5-shared library names
    def cmake_args(self):
        options = super(Openfast, self).cmake_args()
        options.append('-DHDF5_NO_FIND_PACKAGE_CONFIG_FILE:BOOL=ON')
        return options
