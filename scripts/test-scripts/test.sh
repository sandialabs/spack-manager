#!/bin/bash

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e
cmd "export SPACK_MANAGER=${HOME}/exawind/spack-manager"
cmd "source ${SPACK_MANAGER}/start.sh"
set +e
cmd "sspack repo add ${SPACK_MANAGER}/repos/exawind"
set -e
cmd "mkdir -p ${SPACK_MANAGER}/environments/exawind"
cmd "cd ${SPACK_MANAGER}/environments/exawind"
cmd "sspack env create -d ."
cmd "cp ${SPACK_MANAGER}/env-templates/darwin.yaml ${SPACK_MANAGER}/environments/exawind/spack.yaml"
cmd "sspack env activate --sh ."
cmd "sspack buildcache keys -it"
cmd "sspack -e . concretize -f"
cmd "sspack -e . install"
cmd "sspack env deactivate --sh"
