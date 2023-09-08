#!/bin/bash -l
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

# Trap and kill background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

if [[ -z ${SPACK_MANAGER} ]]; then
    printf "\nSPACK_MANAGER not set so setting it to ${PWD}\n"
    cmd "export SPACK_MANAGER=${PWD}"
else
    printf "\nSPACK_MANAGER set to ${SPACK_MANAGER}\n"
fi

printf "\nActivating Spack-Manager...\n"
cmd "source ${SPACK_MANAGER}/start.sh && spack-start"

printf "\nMachine detected as: ${SPACK_MANAGER_MACHINE}\n"

printf "\nSetting up recommended environment for ${SPACK_MANAGER_MACHINE}...\n"
ENV_SCRIPT=${SPACK_MANAGER}/configs/${SPACK_MANAGER_MACHINE}/env.sh
if [[ -f "${ENV_SCRIPT}" ]]; then
  cmd "source ${ENV_SCRIPT}"
fi

printf "\nCreating Spack environment...\n"
if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ] || \
   [ "${SPACK_MANAGER_MACHINE}" == 'summit' ] || \
   [ "${SPACK_MANAGER_MACHINE}" == 'spock' ] || \
   [ "${SPACK_MANAGER_MACHINE}" == 'crusher' ] || \
   [ "${SPACK_MANAGER_MACHINE}" == 'frontier' ] || \
   [ "${SPACK_MANAGER_MACHINE}" == 'sunspot' ] || \
   [ "${SPACK_MANAGER_MACHINE}" == 'perlmutter' ] || \
   [ "${SPACK_MANAGER_MACHINE}" == 'kestrel' ] || \
   [ "${SPACK_MANAGER_MACHINE}" == 'azure' ]; then
  cmd "spack manager create-env -y ${SPACK_MANAGER}/env-templates/exawind_${SPACK_MANAGER_MACHINE}.yaml -d ${SPACK_MANAGER}/environments/exawind-${SPACK_MANAGER_MACHINE}"
else
  cmd "spack manager create-env -s exawind+hypre+openfast+ninja -d ${SPACK_MANAGER}/environments/exawind-${SPACK_MANAGER_MACHINE}"
fi

printf "\nActivating Spack environment...\n"
cmd "spack env activate -d ${SPACK_MANAGER}/environments/exawind-${SPACK_MANAGER_MACHINE}"

# This should happen automatically with no compilers so we could probably remove this
if [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
  cmd "spack compiler find"
fi

printf "\nConcretizing environment...\n"
cmd "spack concretize -f"

printf "\nInstalling environment...\n"
for i in {1..4}; do
  cmd "nice spack install" &
done; wait
if [ "${SPACK_MANAGER_MACHINE}" == 'azure' ]; then
  cmd "spack module refresh tcl -y"
fi
#cmd "spack env depfile -o Makefile"
#cmd "nice make -j8"
#cmd "rm -f Makefile"
