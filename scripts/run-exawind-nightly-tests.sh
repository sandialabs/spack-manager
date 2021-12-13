#!/bin/bash -l

#Scheduled script that invokes the nightly Exawind tests

#Example of cron schedule entries:
#Exawind update spack-manager
#0 0 * * * /bin/bash -c "export ${SPACK_MANAGER}=/projects/ecp/exawind/exawind-testing/spack-manager && cd ${SPACK_MANAGER} && ${SPACK_MANAGER}/scripts/update-spack-manager-repo.sh > ${SPACK_MANAGER}/logs/last-spack-manager-repo-update.txt 2>&1"
#Exawind tests
#10 0 * * * /bin/bash -c "export ${SPACK_MANAGER}=/projects/ecp/exawind/exawind-testing/spack-manager && cd ${SPACK_MANAGER} && ${SPACK_MANAGER}/spack-manager/scripts/run-exawind-nightly-tests.sh > ${SPACK_MANAGER}/logs/last-exawind-test-script-invocation.txt 2>&1"

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

if [[ -z ${SPACK_MANAGER} ]]; then
    echo "SPACK_MANAGER not set so setting it to ${PWD}/spack-manager."
    cmd "export SPACK_MANAGER=${PWD}"
else
    echo "SPACK_MANAGER set to ${SPACK_MANAGER}"
fi

# Activate spack-manager
cmd "source ${SPACK_MANAGER}/start.sh"

EXAWIND_TEST_SCRIPT=${SPACK_MANAGER}/scripts/exawind-tests-script.sh
LOG_DIR=${SPACK_MANAGER}/logs
cd ${LOG_DIR}

cat > ${EXAWIND_TEST_SCRIPT} << '_EOF'
#!/bin/bash -l

# Trap and kill background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

# Setup gold file directories
cmd "rm -rf ${SPACK_MANAGER}/golds/tmp/amr-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/tmp/amr-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/archived/amr-wind"
cmd "rm -rf ${SPACK_MANAGER}/golds/tmp/nalu-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/tmp/nalu-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/archived/nalu-wind"

# Uninstall packages to test
cmd "spack uninstall -a -y exawind-nightly || true"
cmd "spack uninstall -a -y nalu-wind-nightly || true"
cmd "spack uninstall -a -y amr-wind-nightly || true"

# Setup and activate Spack environment
cmd "export EXAWIND_ENV_DIR=${SPACK_MANAGER}/environments/exawind"
YAML_FILE="${SPACK_MANAGER}/env-templates/exawind_${SPACK_MANAGER_MACHINE}_tests.yaml"
cmd "rm -f ${EXAWIND_ENV_DIR}/spack.yaml"
cmd "spack manager create-env -y ${YAML_FILE} -d ${EXAWIND_ENV_DIR}"
cmd "spack env activate ${EXAWIND_ENV_DIR}"

# Concretize environment and run tests
cmd "spack concretize -f"
# Parallelize Spack install DAG
for i in {1..2}; do
  cmd "spack install" &
done; wait

# Save gold files
DATE=$(date +%Y-%m-%d-%H-%M)
cmd "tar -czf ${SPACK_MANAGER}/golds/archived/amr-wind/amr-wind-golds-${DATE}.tar.gz -C ${SPACK_MANAGER}/golds/tmp/amr-wind ."
cmd "tar -czf ${SPACK_MANAGER}/golds/archived/nalu-wind/nalu-wind-golds-${DATE}.tar.gz -C ${SPACK_MANAGER}/golds/tmp/nalu-wind ."
_EOF

if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
  cd ${LOG_DIR} && sbatch -J test-exawind -N 1 -t 4:00:00 -A hfm -p short -o "%x.o%j" --gres=gpu:2 ${EXAWIND_TEST_SCRIPT}
elif [ "${SPACK_MANAGER_MACHINE}" == 'rhodes' ]; then
  cd ${LOG_DIR} && nice -n19 ionice -c3 ${EXAWIND_TEST_SCRIPT} &> "test-exawind-$(date +%Y-%m-%d).log"
elif [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
  cd ${LOG_DIR} && nice -n20 ${EXAWIND_TEST_SCRIPT} &> "test-exawind-$(date +%Y-%m-%d).log"
fi
