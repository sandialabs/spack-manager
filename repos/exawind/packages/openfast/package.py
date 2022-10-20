# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack.pkg.builtin.openfast import Openfast as bOpenfast

class Openfast(bOpenfast):
    patch('hub_seg_fault.patch')
    patch('segfault_message.patch', when='%clang@12.0.1 build_type=RelWithDebInfo')
