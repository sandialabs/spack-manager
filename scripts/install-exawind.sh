#!/bin/bash -l

# Trap and kill background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

MYPWD=${PWD}

if [ "${SPACK_MANAGER_MACHINE}" == 'summit' ]; then
  cmd "module unload xl"
  cmd "module load python/3.7.7"
  cmd "module load binutils"
fi

cmd "export TMPDIR=${MYPWD}/../tmp"
cmd "export SPACK_MANAGER=${MYPWD}/.."
cmd "source ${SPACK_MANAGER}/start.sh"
if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
  cmd "create_machine_spack_environment.py -y ${SPACK_MANAGER}/env-templates/${SPACK_MANAGER_MACHINE}.py -d ${SPACK_MANAGER}/environments/exawind"
else
  cmd "create_machine_spack_environment.py -s exawind+hypre -d ${SPACK_MANAGER}/environments/exawind"
fi
cmd "cd ${SPACK_MANAGER}/environments/exawind"
cmd "spack env activate -d ."
if [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
  cmd "spack compiler find"
fi
cmd "spack concretize -f"
for i in {1..2}; do
  cmd "spack install --dont-restage --keep-stage" &
done; wait
