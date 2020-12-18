# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install nalu-fllc
#
# You can edit this file again by typing:
#
#     spack edit nalu-fllc
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack import *
from spack.pkg.exawind.nalu_wind import NaluWind as bNaluWind


class NaluFllc(bNaluWind):
    """FIXME: Put a proper description of your package here."""

    url      = "https://github.com/psakievich/nalu-wind"
    git      = "https://github.com/psakievich/nalu-wind.git"
    version("fllc", branch="fllc", submodules=True)

