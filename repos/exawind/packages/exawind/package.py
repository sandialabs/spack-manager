from spack import *


class Exawind(BundlePackage):
    """Dummy package for the exawind suite"""

    version('main')
    depends_on('nalu-wind+boost+hypre+tioga+openfast+wind-utils')
    depends_on('amr-wind+openfast+hypre')
    #depends_on('py-stk')
    depends_on('trilinos') # for seacas tools
    depends_on('openfast@master')

