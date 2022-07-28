#!/bin/bash
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

# Expected to be run at top level spack-manager directory
export SPACK_MANAGER=$(pwd)
source ${SPACK_MANAGER}/start.sh
spack-start
spack unit-test --extension scripting
