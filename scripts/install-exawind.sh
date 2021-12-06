#!/bin/bash -l

# Trap and kill background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

MYPWD=${PWD}

cmd "export TMPDIR=${MYPWD}/../tmp"
cmd "export SPACK_MANAGER=${MYPWD}/.."
cmd "source ${SPACK_MANAGER}/start.sh"

if [ "${SPACK_MANAGER_MACHINE}" == 'summit' ]; then
  cmd "module unload xl"
  cmd "module load python/3.7.7"
  cmd "module load binutils"
elif [ "${SPACK_MANAGER_MACHINE}" == 'spock' ]; then
  cmd "module load binutils"
elif [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
  cmd "source /nopt/nrel/ecom/hpacf/env.sh"
fi

if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ] || [ "${SPACK_MANAGER_MACHINE}" == 'summit' ]; then
  cmd "spack manager create-env -y ${SPACK_MANAGER}/env-templates/exawind_matrix.yaml -d ${SPACK_MANAGER}/environments/exawind"
elif [ "${SPACK_MANAGER_MACHINE}" == 'spock' ]; then
  cmd "spack manager create-env -y ${SPACK_MANAGER}/env-templates/exawind_spock.yaml -d ${SPACK_MANAGER}/environments/exawind"
else
  cmd "spack manager create-env -s exawind+hypre -d ${SPACK_MANAGER}/environments/exawind"
fi

cmd "cd ${SPACK_MANAGER}/environments/exawind"
cmd "spack env activate -d ."

if [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
  cmd "spack compiler find"
fi

cmd "spack concretize -f"

for i in {1..2}; do
  cmd "nice spack install" &
done; wait
