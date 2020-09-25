from spack import *
from spack.pkg.builtin.boost import Boost as bBoost

class Boost(bBoost):
    variant('cxxstd',
            default='14',
            values=('98', '11', '14', '17', '2a'),
            multi=False,
            description='Use the specified C++ standard when building.')
