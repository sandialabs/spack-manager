#!/bin/bash

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e
cmd "export SPACK_MANAGER=${HOME}/exawind/spack-manager"
cmd "source ${SPACK_MANAGER}/start.sh"
cmd "mkdir -p ${SPACK_MANAGER}/environments/exawind"
#cmd "mkdir -p ${SPACK_MANAGER}/tmp/tmp_golds/amr-wind"
cmd "cd ${SPACK_MANAGER}/environments/exawind"
cmd "spack env create -d ."
cmd "cp ${SPACK_MANAGER}/env-templates/darwin.yaml ${SPACK_MANAGER}/environments/exawind/spack.yaml"
cmd "spack env activate --sh ."
set +e
#cmd "spack uninstall -a -y amr-wind-nightly"
#cmd "spack uninstall -a -y nalu-wind-nightly"
#cmd "spack uninstall -a -y --dependents trilinos"
cmd "spack uninstall -a -y exawind-nightly"
set -e
#cmd "spack mirror add e4s https://cache.e4s.io"
#cmd "spack buildcache keys -it"
cmd "spack -e . concretize -f"
cmd "spack -e . install"
#(set -x; tar -czf ${SPACK_MANAGER}/golds/archived/amr-wind/amr_wind_golds-$(date +%Y-%m-%d-%H-%M).tar.gz -C ${SPACK_MANAGER}/tmp/tmp_golds/amr-wind .)
#cmd "rm -rf ${SPACK_MANAGER}/tmp/tmp_golds/amr-wind"
