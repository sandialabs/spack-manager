from spack.package import *
from spack.pkg.exawind.openfast import Openfast


class OpenfastFsi(Openfast):
    """OpenFAST instance for using FSI"""

    git = "https://github.com/gantech/openfast"
    homepage = git
    url = git

    version("master", branch="f/br_fsi_2")

