#!/bin/bash -l

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
cmd "mkdir -p ${SPACK_MANAGER}/environments/exawind"
cmd "cd ${SPACK_MANAGER}/environments/exawind"
cmd "spack env create -d ."
cmd "cp ${SPACK_MANAGER}/env-templates/${SPACK_MANAGER_MACHINE}.yaml ${SPACK_MANAGER}/environments/exawind/spack.yaml"
cmd "spack env activate --sh ."
cmd "spack -e . concretize -f"
cmd "spack -e . install --no-cache"
