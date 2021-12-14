#!/bin/bash -l

#Scheduled script that invokes the nightly Exawind tests

#Example of cron schedule entries:
#Exawind update spack-manager
#0 0 * * * /bin/bash -c "export SPACK_MANAGER=/projects/ecp/exawind/exawind-testing/spack-manager && cd \${SPACK_MANAGER} && \${SPACK_MANAGER}/scripts/update-spack-manager-repo.sh > \${SPACK_MANAGER}/logs/last-spack-manager-repo-update.txt 2>&1"
#Exawind tests
#10 0 * * * /bin/bash -c "export SPACK_MANAGER=/projects/ecp/exawind/exawind-testing/spack-manager && cd \${SPACK_MANAGER} && \${SPACK_MANAGER}/scripts/run-exawind-nightly-tests.sh > \${SPACK_MANAGER}/logs/last-exawind-test-script-invocation.txt 2>&1"

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

echo "Starting at $(date).\n"

if [[ -z ${SPACK_MANAGER} ]]; then
    echo "SPACK_MANAGER not set so setting it to ${PWD}/spack-manager."
    cmd "export SPACK_MANAGER=${PWD}"
else
    echo "SPACK_MANAGER set to ${SPACK_MANAGER}"
fi

echo "Activating Spack-Manager..."
cmd "source ${SPACK_MANAGER}/start.sh"

EXAWIND_TEST_SCRIPT=${SPACK_MANAGER}/scripts/exawind-tests-script.sh

echo "Generating test script for submission..."
cat > ${EXAWIND_TEST_SCRIPT} << '_EOF'
#!/bin/bash -l

# Trap and kill background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

echo "Starting at $(date).\n"

echo "Setting up gold files directories..."
cmd "rm -rf ${SPACK_MANAGER}/golds/tmp/amr-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/tmp/amr-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/archived/amr-wind"
cmd "rm -rf ${SPACK_MANAGER}/golds/tmp/nalu-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/tmp/nalu-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/archived/nalu-wind"

echo "Uninstall nightly test packages..."
cmd "spack uninstall -a -y exawind-nightly || true"
cmd "spack uninstall -a -y nalu-wind-nightly || true"
cmd "spack uninstall -a -y amr-wind-nightly || true"

echo "Setting up and activating Spack environoment..."
cmd "export EXAWIND_ENV_DIR=${SPACK_MANAGER}/environments/exawind"
YAML_FILE="${SPACK_MANAGER}/env-templates/exawind_${SPACK_MANAGER_MACHINE}_tests.yaml"
cmd "rm -f ${EXAWIND_ENV_DIR}/spack.yaml"
cmd "spack manager create-env -y ${YAML_FILE} -d ${EXAWIND_ENV_DIR}"
cmd "spack env activate ${EXAWIND_ENV_DIR}"

echo "Running the tests..."
cmd "spack concretize -f"
# Parallelize Spack install DAG
for i in {1..2}; do
  cmd "spack install" &
done; wait

# Save gold files
echo "Saving gold files..."
DATE=$(date +%Y-%m-%d-%H-%M)
cmd "tar -czf ${SPACK_MANAGER}/golds/archived/amr-wind/amr-wind-golds-${DATE}.tar.gz -C ${SPACK_MANAGER}/golds/tmp/amr-wind ."
cmd "tar -czf ${SPACK_MANAGER}/golds/archived/nalu-wind/nalu-wind-golds-${DATE}.tar.gz -C ${SPACK_MANAGER}/golds/tmp/nalu-wind ."

echo "\nDone at $(date)."
_EOF

cmd "chmod u+x ${EXAWIND_TEST_SCRIPT}"

LOG_DIR=${SPACK_MANAGER}/logs
DATE=$(date +%Y-%m-%d)

if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
  (set -x; cd ${LOG_DIR} && sbatch -J test-exawind-${DATE} -N 1 -t 4:00:00 -A hfm -p short -o "%x.o%j" --gres=gpu:2 ${EXAWIND_TEST_SCRIPT})
elif [ "${SPACK_MANAGER_MACHINE}" == 'rhodes' ]; then
  (set -x; cd ${LOG_DIR} && nice -n19 ionice -c3 ${EXAWIND_TEST_SCRIPT} &> test-exawind-${DATE}.log)
elif [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
  (set -x; cd ${LOG_DIR} && nice -n20 ${EXAWIND_TEST_SCRIPT} &> test-exawind-${DATE}.log)
fi

echo "\nDone at $(date)."
