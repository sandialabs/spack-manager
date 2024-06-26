# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

"""
a script to make sure minimum requirements for spack-manager
are met.

- python@3.8 or higher
"""
import sys


def check_spack_manager_requirements():
    if sys.version_info < (3, 8):
        raise ValueError("Spack-Manager requires Python 3.8 or higher.")


if __name__ == "__main__":
    check_spack_manager_requirements()
