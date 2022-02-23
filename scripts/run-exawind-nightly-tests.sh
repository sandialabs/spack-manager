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

printf "\nGenerating test script for submission...\n"
EXAWIND_TEST_SCRIPT=${SPACK_MANAGER}/scripts/exawind-tests-script.sh
cat > ${EXAWIND_TEST_SCRIPT} << '_EOF'
#!/bin/bash -l

# Trap and kill background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

printf "Starting at $(date)\n"

printf "\nSetting up recommended environment for machine...\n"
ENV_SCRIPT=${SPACK_MANAGER}/configs/${SPACK_MANAGER_MACHINE}/env.sh
if [[ -f "${ENV_SCRIPT}" ]]; then
  cmd "source ${ENV_SCRIPT}"
fi

printf "\nSetting up gold files directories...\n"
cmd "rm -rf ${SPACK_MANAGER}/golds/tmp/amr-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/tmp/amr-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/archived/amr-wind"
cmd "rm -rf ${SPACK_MANAGER}/golds/tmp/nalu-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/tmp/nalu-wind"
cmd "mkdir -p ${SPACK_MANAGER}/golds/archived/nalu-wind"

printf "\nSetting up Spack environoment...\n"
cmd "export EXAWIND_ENV_DIR=${SPACK_MANAGER}/environments/exawind"
YAML_FILE="${SPACK_MANAGER}/env-templates/exawind_${SPACK_MANAGER_MACHINE}_tests.yaml"
cmd "spack manager create-env -y ${YAML_FILE} -d ${EXAWIND_ENV_DIR}"

printf "\nUpdating git repos in selected stage directories...\n"
cmd "spack env activate -d ${EXAWIND_ENV_DIR}"
cmd "${SPACK_MANAGER}/scripts/stage-updater.py -e ${SPACK_MANAGER}/environments/exawind"
cmd "spack env deactivate"

printf "\nUninstall nightly test packages...\n"
cmd "spack uninstall -a -y exawind-nightly || true"
cmd "spack uninstall -a -y nalu-wind-nightly || true"
cmd "spack uninstall -a -y amr-wind-nightly || true"
cmd "spack uninstall -a -y trilinos || true"
cmd "spack uninstall -a -y hypre || true"

printf "\nConcretizing environment...\n"
cmd "spack env activate -d ${EXAWIND_ENV_DIR}"
cmd "spack concretize -f"

# Develop spec stuff that isn't working as desired
#DEVELOP_SPEC_DIR=${SPACK_MANAGER}/stage/develop-specs/amr-wind-nightly
#if [[ -d ${DEVELOP_SPEC_DIR} ]]; then
#  cmd "spack develop -p ${DEVELOP_SPEC_DIR} --no-clone amr-wind-nightly@main"
#else
#  cmd "spack develop -p ${DEVELOP_SPEC_DIR} --clone amr-wind-nightly@main"
#fi
#DEVELOP_SPEC_DIR=${SPACK_MANAGER}/stage/develop-specs/hypre
#if [[ -d ${DEVELOP_SPEC_DIR} ]]; then
#  cmd "spack develop -p ${DEVELOP_SPEC_DIR} --no-clone hypre@develop"
#else
#  cmd "spack develop -p ${DEVELOP_SPEC_DIR} --clone hypre@develop"
#fi

printf "\nTests started at: $(date)\n\n"
printf "spack install --dont-restage --keep-stage\n"
time (for i in {1..4}; do spack install --dont-restage --keep-stage & done; wait)
#cmd "time spack install --dont-restage --keep-stage"
printf "\nTests ended at: $(date)\n"

printf "\nSaving gold files...\n"
DATE=$(date +%Y-%m-%d-%H-%M)
cmd "tar -czf ${SPACK_MANAGER}/golds/archived/amr-wind/amr-wind-golds-${DATE}.tar.gz -C ${SPACK_MANAGER}/golds/tmp/amr-wind ."
cmd "tar -czf ${SPACK_MANAGER}/golds/archived/nalu-wind/nalu-wind-golds-${DATE}.tar.gz -C ${SPACK_MANAGER}/golds/tmp/nalu-wind ."

STAGE_DIR=$(spack location -S)
if [ ! -z "${STAGE_DIR}" ]; then
  #Haven't been able to find another robust way to rm with exclude
  printf "\nRemoving all unused staged directories...\n"
  cmd "cd ${STAGE_DIR} && rm -rf resource* spack-stage-b* spack-stage-c* spack-stage-d* spack-stage-f* spack-stage-g* spack-stage-h* spack-stage-i* spack-stage-j* spack-stage-k* spack-stage-l* spack-stage-m* spack-stage-nc* spack-stage-net* spack-stage-o* spack-stage-p* spack-stage-q* spack-stage-r* spack-stage-s* spack-stage-tar* spack-stage-ti* spack-stage-u* spack-stage-v* spack-stage-w* spack-stage-x* spack-stage-y* spack-stage-z*"
  #Would like something like this
  #find ${STAGE_DIR}/ -maxdepth 0 -type d -not -name "spack-stage-trilinos*" -exec rm -r {} \;
fi

printf "\nDeactivating environment...\n"
cmd "spack env deactivate"

printf "\nDone at $(date)\n"
_EOF

cmd "chmod u+x ${EXAWIND_TEST_SCRIPT}"

printf "\nRunning test script...\n"
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
