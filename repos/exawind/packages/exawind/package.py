from spack import *


class Exawind(Package):
    """Dummy package for the exawind suite"""

    homepage = "https://github.com/Exawind"
    url      = "exawind"

    version('main')

    maintainers = ['jrood-nrel', 'psakiev']

    depends_on('nalu-wind+hypre+tioga+openfast+wind-utils')
    depends_on('amr-wind+openfast+hypre')
    depends_on('py-stk')
    depends_on('trilinos') # for seacas tools
    depends_on('openfast@master')

    def install(self, spec, prefix):
        pass
