#!/bin/bash

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

cmd "export SPACK_MANAGER=${HOME}/exawind/spack-manager"
cmd "source ${SPACK_MANAGER}/start.sh"
cmd "mkdir -p ${SPACK_MANAGER}/golds/tmp/amr-wind"
cmd "spack uninstall -a -y amr-wind-nightly || true"
cmd "export EXAWIND_TEST_DIR=${SPACK_MANAGER}/environments/exawind"
cmd "spack manager create-env -d ${EXAWIND_TEST_DIR} -s amr-wind-nightly"
cmd "spack env activate ${EXAWIND_TEST_DIR}"
cmd "nice spack concretize -f"
cmd "nice -n19 ionice -c3 spack install"
DATE=$(date +%Y-%m-%d-%H-%M)
cmd "mkdir -p ${SPACK_MANAGER}/golds/archived/amr-wind"
cmd "tar -czf ${SPACK_MANAGER}/golds/archived/amr-wind/amr_wind_golds-${DATE}.tar.gz -C ${SPACK_MANAGER}/golds/tmp/amr-wind ."
cmd "rm -rf ${SPACK_MANAGER}/golds/tmp/amr-wind"
