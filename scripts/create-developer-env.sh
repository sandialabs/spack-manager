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

# Options
COMPILER="gcc"
DEV_PACKAGE="nalu-wind"
VERSION="master"
SPEC="${DEV_PACKAGE}@${VERSION}%${COMPILER}"

printf "\nCreating developer environment...\n"
if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
  SNAPSHOT_DIR="/projects/exawind/exawind-snapshots/environment-latest"
elif [ "${SPACK_MANAGER_MACHINE}" == 'rhodes' ]; then
  SNAPSHOT_DIR="/projects/ecp/exawind/exawind-snapshots/environment-latest"
fi
cmd "spack manager create-env --directory ${SPACK_MANAGER}/environments/exawind --spec ${SPEC}"
cmd "spack env activate -d ${SPACK_MANAGER}/environments/exawind"
cmd "spack config add config:concretizer:original"
cmd "spack manager external ${SNAPSHOT_DIR} -v ${COMPILER} --blacklist ${DEV_PACKAGE}"
cmd "spack manager develop ${SPEC}"
cmd "spack concretize -f"
cmd "spack install"

printf "\nDone at $(date)\n"
