#!/bin/bash -l

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
cmd "source ${SPACK_MANAGER}/start.sh"

printf "\nMachine detected as: ${SPACK_MANAGER_MACHINE}\n"

printf "\nSetting up recommended environment for ${SPACK_MANAGER_MACHINE}...\n"
ENV_SCRIPT=${SPACK_MANAGER}/configs/${SPACK_MANAGER_MACHINE}/env.sh
if [[ -f "${ENV_SCRIPT}" ]]; then
  cmd "source ${ENV_SCRIPT}"
fi

printf "\nCreating Spack environment...\n"
if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ] || [ "${SPACK_MANAGER_MACHINE}" == 'summit' ]; then
  cmd "spack manager create-env -y ${SPACK_MANAGER}/env-templates/exawind_matrix.yaml -d ${SPACK_MANAGER}/environments/exawind"
elif [ "${SPACK_MANAGER_MACHINE}" == 'spock' ]; then
  cmd "spack manager create-env -y ${SPACK_MANAGER}/env-templates/exawind_spock.yaml -d ${SPACK_MANAGER}/environments/exawind"
else
  cmd "spack manager create-env -s exawind+hypre -d ${SPACK_MANAGER}/environments/exawind"
fi

printf "\nActivating Spack environment...\n"
cmd "spack env activate -d ${SPACK_MANAGER}/environments/exawind"

if [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
  cmd "spack compiler find"
fi

printf "\nConcretizing environment...\n"
cmd "spack concretize -f"

printf "\nInstalling environment...\n"
for i in {1..2}; do
  cmd "nice spack install" &
done; wait
