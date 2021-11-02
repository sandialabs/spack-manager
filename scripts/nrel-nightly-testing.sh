#!/bin/bash

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e
cmd "export SPACK_MANAGER=${HOME}/exawind/spack-manager"
cmd "source ${SPACK_MANAGER}/start.sh"
cmd "spack uninstall -a -y exawind-nightly"
#cmd "mkdir -p ${SPACK_MANAGER}/tmp/tmp_golds/amr-wind"
cmd "export EXAWIND_TEST_DIR=${SPACK_MANAGER}/environments/exawind"
cmd "spack manager create-env -d ${EXAWIND_TEST_DIR} -s exawind-nightly"
cmd "spack env activate ${EXAWIND_TEST_DIR}"
set +e
#cmd "spack uninstall -a -y amr-wind-nightly"
#cmd "spack uninstall -a -y nalu-wind-nightly"
#cmd "spack uninstall -a -y --dependents trilinos"
set -e
#cmd "spack mirror add e4s https://cache.e4s.io"
#cmd "spack buildcache keys -it"
cmd "spack concretize -f"
cmd "spack install"
#(set -x; tar -czf ${SPACK_MANAGER}/golds/archived/amr-wind/amr_wind_golds-$(date +%Y-%m-%d-%H-%M).tar.gz -C ${SPACK_MANAGER}/tmp/tmp_golds/amr-wind .)
#cmd "rm -rf ${SPACK_MANAGER}/tmp/tmp_golds/amr-wind"
