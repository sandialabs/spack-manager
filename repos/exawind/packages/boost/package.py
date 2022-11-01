# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.pkg.builtin.boost import Boost as bBoost

class Boost(bBoost):
    # Avoid the build system not finding static -lm -ldl etc
    patch("intel-no-static.patch", when="@1.76.0:%intel")
