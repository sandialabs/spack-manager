#!/bin/bash -l

#Script that creates a new shared snapshot for Exawind software

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

printf "\nRunning snapshot creator...\n"
cmd "nice -n19 ${SPACK_MANAGER}/scripts/snapshot_creator.py --use_develop --modules --use_machine_name --num_threads 4"

printf "\nDone at $(date)\n"
