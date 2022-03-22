#!/bin/bash -l

#Scheduled script that invokes the nightly Exawind tests

#Example of cron schedule entry:
#0 0 * * * /bin/bash -c "export SPACK_MANAGER=/projects/ecp/exawind/exawind-testing/spack-manager && cd \${SPACK_MANAGER} && \${SPACK_MANAGER}/scripts/update-spack-manager-repo.sh &> \${SPACK_MANAGER}/logs/last-spack-manager-repo-update.txt && \${SPACK_MANAGER}/scripts/run-exawind-nightly-tests.sh &> \${SPACK_MANAGER}/logs/last-exawind-test-script-invocation.txt"
# or just run it when in the spack-manager directory as ./scripts/run-exawind-nightly-tests.sh

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

printf "Starting at $(date).\n"

if [[ -z ${SPACK_MANAGER} ]]; then
    printf "\nSPACK_MANAGER not set so setting it to ${PWD}\n"
    cmd "export SPACK_MANAGER=${PWD}"
else
    printf "\nSPACK_MANAGER set to ${SPACK_MANAGER}\n"
fi

printf "\nActivating Spack-Manager...\n"
cmd "source ${SPACK_MANAGER}/start.sh && spack-start"

printf "\nRunning test script...\n"
EXAWIND_TEST_SCRIPT=${SPACK_MANAGER}/scripts/exawind-tests-script.sh
LOG_DIR=${SPACK_MANAGER}/logs
DATE=$(date +%Y-%m-%d)
if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
  (set -x; cd ${LOG_DIR} && sbatch -J test-exawind-${DATE} -N 1 -t 4:00:00 -A exawind -p short -o "%x.o%j" --gres=gpu:2 ${EXAWIND_TEST_SCRIPT})
elif [ "${SPACK_MANAGER_MACHINE}" == 'rhodes' ]; then
  (set -x; cd ${LOG_DIR} && nice -n19 ionice -c3 ${EXAWIND_TEST_SCRIPT} &> test-exawind-${DATE}.log)
elif [ "${SPACK_MANAGER_MACHINE}" == 'ascicgpu' ]; then
  (set -x; cd ${LOG_DIR} && nice -n19 ionice -c3 ${EXAWIND_TEST_SCRIPT} &> test-exawind-${DATE}.log)
elif [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
  (set -x; cd ${LOG_DIR} && nice -n20 ${EXAWIND_TEST_SCRIPT} &> test-exawind-${DATE}.log)
fi

printf "\nDone at $(date)\n"
