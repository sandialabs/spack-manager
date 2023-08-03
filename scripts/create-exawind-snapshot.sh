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

# default to 8 core build
NUM_CORES=8

printf "\nRunning snapshot creator...\n"
if [[ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]]; then
  # TODO get cores right on these machines
  NUM_CORES=16
  cmd "nice -n19 spack manager snapshot -m -s exawind%gcc+hypre+openfast~cuda exawind%intel+hypre+openfast exawind%clang+hypre+openfast exawind%gcc+hypre+openfast+cuda+amr_wind_gpu+nalu_wind_gpu"
elif [[ "${SPACK_MANAGER_MACHINE}" == "e4s" ]]; then
  NUM_CORES=8
  cmd "nice -n19 spack manager snapshot -m -s exawind+hypre+openfast amr-wind+hypre+openfast+masa"
elif [[ "${SPACK_MANAGER_MACHINE}" == "rhodes" ]]; then
  NUM_CORES=16
  cmd "nice -n19 spack manager snapshot -m -s exawind%gcc+hypre+openfast exawind%intel+hypre+openfast exawind%clang+hypre+openfast"
elif [[ "${SPACK_MANAGER_MACHINE}" == "summit" ]]; then
  NUM_CORES=8
  cmd "nice -n19 spack manager snapshot -m -s exawind%gcc+hypre+cuda+amr_wind_gpu+nalu_wind_gpu exawind%gcc+hypre~cuda"
elif [[ "${SPACK_MANAGER_MACHINE}" == "perlmutter" ]]; then
  NUM_CORES=8
  cmd "nice -n19 spack manager snapshot -m -s exawind%gcc+hypre+cuda+amr_wind_gpu+nalu_wind_gpu"
elif [[ "${SPACK_MANAGER_MACHINE}" == "snl-hpc" ]]; then
  # TODO we should probably launch the install through slurm and exit on this one
  cmd "nice -n19 spack manager snapshot -s exawind+hypre+openfast amr-wind+hypre+openfast"
else
  cmd "nice -n19 spack manager snapshot -s exawind+hypre+openfast"
fi

printf "\nActivating snapshot environment...\n"
cmd "spack env activate -d ${SPACK_MANAGER}/snapshots/exawind/${SPACK_MANAGER_MACHINE}/$(date +%Y-%m-%d)"

printf "\nInstalling environment...\n"
time (
  for i in {1..1}; do
      nice -n19 spack install &
  done
  wait
)

printf "\nCreate modules...\n"
cmd "spack module lmod refresh -y"
cmd "spack module tcl refresh -y"

cmd "spack env deactivate"

printf "\nDone at $(date)\n"
