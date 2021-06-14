from spack import *


class ExawindNightly(BundlePackage):
    """Dummy package for nightly tests of the exawind suite"""
    version('main')

    variant('host_name', default='default')
    variant('extra_name', default='')


    hn = self.spec.variants['host_name'].value
    en = self.spec.variants['extra_name'].value

    depends_on('nalu-wind-nightly+hypre+tioga+openfast+wind-utils')
    depends_on('amr-wind-nightly+openfast+hypre')
    depends_on('trilinos') # for seacas tools
    depends_on('openfast@master')
