#!/bin/bash -l

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

cmd "export TMPDIR=${MEMBERWORK}/cfd116/.tmp"
cmd "module load python/3.7.7"
cmd "module unload xl"
cmd "module load gcc/10.2.0"
cmd "mpicc --version"
cmd "export SPACK_MANAGER=${PROJWORK}/cfd116/jrood/spack-manager"
cmd "source ${SPACK_MANAGER}/start.sh"
cmd "mkdir -p ${SPACK_MANAGER}/environments/exawind"
cmd "cd ${SPACK_MANAGER}/environments/exawind"
cmd "spack env create -d ."
cmd "cp ${SPACK_MANAGER}/env-templates/summit.yaml ${SPACK_MANAGER}/environments/exawind/spack.yaml"
cmd "spack env activate --sh ."
#cmd "spack -e . buildcache keys -it"
cmd "spack -e . concretize -f"
cmd "spack -e . install --no-cache"
