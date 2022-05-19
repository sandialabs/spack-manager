#!/bin/bash -l
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

#Script that shows an example of creating a developer environment from a shared snapshot for Exawind software

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

printf "Starting at $(date).\n"

if [[ -z ${SPACK_MANAGER} ]]; then
  printf "\nSPACK_MANAGER not set so setting it to ${PWD}\n"
  cmd "export SPACK_MANAGER=${PWD}"
else
  printf "\nSPACK_MANAGER set to ${SPACK_MANAGER}\n"
fi

printf "\nActivating Spack-Manager...\n"
cmd "source ${SPACK_MANAGER}/start.sh && spack-start"

printf "\nCreating developer environment...\n"
if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
  COMPILER='gcc'
  SPEC="nalu-wind@master+hypre+cuda cuda_arch=70 %${COMPILER}"
  DEV_COMMAND='spack manager develop nalu-wind@master; spack manager develop hypre@develop'
elif [ "${SPACK_MANAGER_MACHINE}" == 'rhodes' ]; then
  COMPILER='gcc'
  SPEC="nalu-wind@master+hypre %${COMPILER}"
  DEV_COMMAND='spack manager develop nalu-wind@master; spack manager develop hypre@develop'
fi

cmd "spack manager create-env --name exawind --spec '${SPEC}'"
cmd "spack env activate -d ${SPACK_MANAGER}/environments/exawind"
cmd "${DEV_COMMAND}"
cmd "spack manager external --latest"
cmd "spack concretize -f"
cmd "spack install"

printf "\nDone at $(date)\n"
