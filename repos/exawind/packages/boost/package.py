from spack import *
from spack.pkg.builtin.boost import Boost as bBoost

class Boost(bBoost):
    # Avoid the build system not finding static -lm -ldl etc
    patch('intel-no-static.patch', when='@1.76.0:%intel')
