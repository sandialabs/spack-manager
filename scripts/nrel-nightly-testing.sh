#!/bin/bash -l

# Trap and kill background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

# Activate spack-manager
cmd "export SPACK_MANAGER=${HOME}/exawind/spack-manager"
cmd "source ${SPACK_MANAGER}/start.sh"

# Setup gold file directories
cmd "rm -rf ${SPACK_MANAGER}/golds/tmp/amr-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/tmp/amr-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/archived/amr-wind"
cmd "rm -rf ${SPACK_MANAGER}/golds/tmp/nalu-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/tmp/nalu-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/archived/nalu-wind"

# Setup and activate Spack environment
cmd "export EXAWIND_ENV_DIR=${SPACK_MANAGER}/environments/exawind"
YAML_FILE="${SPACK_MANAGER}/env-templates/exawind_${SPACK_MANAGER_MACHINE}_tests.yaml"
cmd "spack manager create-env -y ${YAML_FILE} -d ${EXAWIND_ENV_DIR}"
cmd "spack env activate ${EXAWIND_ENV_DIR}"

# Uninstall packages to test
cmd "nice -n19 ionice -c3 spack uninstall -a -y exawind-nightly || true"
cmd "nice -n19 ionice -c3 spack uninstall -a -y nalu-wind-nightly || true"
cmd "nice -n19 ionice -c3 spack uninstall -a -y amr-wind-nightly || true"

# Concretize environment and run tests
cmd "nice -n19 ionice -c3 spack concretize -f"
for i in {1..2}; do
  cmd "nice -n19 ionice -c3 spack install" &
done; wait

# Save gold files
DATE=$(date +%Y-%m-%d-%H-%M)
cmd "nice -n19 ionice -c3 tar -czf ${SPACK_MANAGER}/golds/archived/amr-wind/amr-wind-golds-${DATE}.tar.gz -C ${SPACK_MANAGER}/golds/tmp/amr-wind ."
cmd "nice -n19 ionice -c3 tar -czf ${SPACK_MANAGER}/golds/archived/nalu-wind/nalu-wind-golds-${DATE}.tar.gz -C ${SPACK_MANAGER}/golds/tmp/nalu-wind ."
