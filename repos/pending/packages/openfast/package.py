from spack.pkg.builtin.openfast import Openfast as bOpenfast

class Openfast(bOpenfast):
    version('develop', branch='dev')
    version('master', branch='main')
    version('2.6.0', tag='v2.6.0')
    version('2.5.0', tag='v2.5.0')
    version('2.4.0', tag='v2.4.0')
    version('2.3.0', tag='v2.3.0')
    version('2.2.0', tag='v2.2.0')
    version('2.1.0', tag='v2.1.0')
    version('2.0.0', tag='v2.0.0')
    version('1.0.0', tag='v1.0.0')

    # Avoid using HDF5's installed CMake config with hdf5-shared library names
    def cmake_args(self):
        options = super(Openfast, self).cmake_args()
        options.append('-DHDF5_NO_FIND_PACKAGE_CONFIG_FILE:BOOL=ON')
        return options
