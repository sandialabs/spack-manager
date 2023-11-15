# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os
import sys

# required to get the modules in the manager directory to show up
module_dir = os.path.realpath(os.path.abspath(os.path.join(__file__, "..", "..", "manager")))
sys.path.append(module_dir)
