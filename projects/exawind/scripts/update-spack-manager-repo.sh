#!/bin/bash -l
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

# Script for updating the spack-manager repo before it's used in running the tests.

printf "Job is running on ${HOSTNAME}\n"
printf "\nRun at $(date)\n"
printf "\nUpdating spack-manager repo...\n"
(set -x; pwd; git fetch --all; git reset --hard origin/main; git clean -df; git submodule update; git status -uno) 2>&1
