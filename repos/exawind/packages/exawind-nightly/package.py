from spack import *


class ExawindNightly(BundlePackage):
    """Dummy package for nightly tests of the exawind suite"""
    version('main')


    depends_on('nalu-wind-nightly+hypre+tioga+openfast+wind-utils')
    depends_on('amr-wind-nightly+openfast+hypre')
    depends_on('trilinos') # for seacas tools
    depends_on('openfast@master')
