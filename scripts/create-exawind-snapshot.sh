#!/bin/bash -l

#Script that creates a new shared snapshot for Exawind software

# Trap and kill background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

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

printf "\nRunning snapshot creator...\n"
cmd "nice -n19 ${SPACK_MANAGER}/scripts/snapshot_creator.py --use_develop --modules --use_machine_name --stop_after concretize"

printf "\nActivating snapshot environment...\n"
cmd "spack env activate -d ${SPACK_MANAGER}/environments/exawind/snapshots/${SPACK_MANAGER_MACHINE}/$(date +%Y-%m-%d)"

printf "\nInstalling environment...\n"
time (for i in {1..4}; do nice -n19 spack install & done; wait)

printf "\nCreate modules...\n"
cmd "spack module tcl refresh -y"

cmd "spack env deactivate"

printf "\nDone at $(date)\n"
