#!/bin/bash -l
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

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

cmd "export SPACK_MANAGER_CLEAN_HYPRE=true"
# Shouldn't use parallel DAG unless git hash installs work or hypre uses CMake
# due to hypre using autotools which can't handle multiple concurrent builds

printf "\nRunning snapshot creator...\n"
if [[ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]]; then
  cmd "unset SPACK_MANAGER_CLEAN_HYPRE"
  cmd "nice -n19 ${SPACK_MANAGER}/scripts/snapshot_creator.py --use_develop --modules --use_machine_name --stop_after concretize --link_type soft"
elif [[ "${SPACK_MANAGER_MACHINE}" == "e4s" ]]; then
  cmd "unset SPACK_MANAGER_CLEAN_HYPRE"
  cmd "nice -n19 ${SPACK_MANAGER}/scripts/snapshot_creator.py --modules --use_machine_name --stop_after concretize --link_type soft"
else
  cmd "nice -n19 ${SPACK_MANAGER}/scripts/snapshot_creator.py --use_develop --modules --use_machine_name --stop_after concretize"
fi

printf "\nActivating snapshot environment...\n"
cmd "spack env activate -d ${SPACK_MANAGER}/environments/exawind/snapshots/${SPACK_MANAGER_MACHINE}/$(date +%Y-%m-%d)"

printf "\nInstalling environment...\n"
time (
  for i in {1..1}; do
    nice -n19 spack install &
  done
  wait
)

printf "\nCreate modules...\n"
cmd "spack module tcl refresh -y"

cmd "spack env deactivate"

printf "\nDone at $(date)\n"
