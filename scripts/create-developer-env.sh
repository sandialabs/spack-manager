#!/bin/bash -l

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
cmd "source ${SPACK_MANAGER}/start.sh"

printf "\nCreating developer environment...\n"
SNAPSHOT_DIR="${HOME}/exawind/spack-manager/environments/exawind/snapshots/rhodes/2022-01-25"
cmd "spack manager create-env --directory ${SPACK_MANAGER}/environments/exawind --spec nalu-wind%gcc"
cmd "sed -i 's/clingo/original/g' ${SPACK_MANAGER}/environments/exawind/include.yaml"
cmd "spack env activate -d ${SPACK_MANAGER}/environments/exawind"
cmd "spack manager external ${SNAPSHOT_DIR} -v gcc --blacklist nalu-wind"
cmd "spack manager develop nalu-wind@master%gcc"
cmd "spack concretize -f"
cmd "spack install"

printf "\nDone at $(date)\n"
