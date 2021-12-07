#!/bin/bash

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

cmd "export SPACK_MANAGER=${HOME}/exawind/spack-manager"
cmd "source ${SPACK_MANAGER}/start.sh"
cmd "spack uninstall -a -y amr-wind-nightly || true"
cmd "export EXAWIND_TEST_DIR=${SPACK_MANAGER}/environments/exawind"
cmd "spack manager create-env -d ${EXAWIND_TEST_DIR} -s amr-wind-nightly"
cmd "spack env activate ${EXAWIND_TEST_DIR}"
cmd "nice spack concretize -f"
cmd "nice -n19 ionice -c3 spack install"
