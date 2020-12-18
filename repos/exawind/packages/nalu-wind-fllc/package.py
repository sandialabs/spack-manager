from spack import *
from spack.pkg.exawind.nalu_wind import NaluWind as bNaluWind
import spack.config
import os
from shutil import copyfile
import inspect
import re
from spack.util.executable import ProcessError


class NaluWindFllc(bNaluWind, CudaPackage):
    maintainers = ['psakievich']
    git      = "https://github.com/psakievich/nalu-wind.git"

    generator = 'Unix Makefiles'
    version('master', branch='fllc')

