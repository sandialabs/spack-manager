#!/bin/bash -l
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

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

if [[ -z ${SPACK_MANAGER_GOLDS_DIR} ]]; then
    printf "\nSPACK_MANAGER_GOLDS_DIR not set so setting it to ${SPACK_MANAGER}/golds\n"
    cmd "export SPACK_MANAGER_GOLDS_DIR=${SPACK_MANAGER}/golds"
else
    printf "\nSPACK_MANAGER_GOLDS_DIR set to ${SPACK_MANAGER_GOLDS_DIR}\n"
fi

printf "\nActivating Spack-Manager...\n"
cmd "source ${SPACK_MANAGER}/start.sh && spack-start"

printf "\nCleaning Spack installation...\n"
  echo "Remove Spack-Manager cache:"
  cmd "rm -rf ${SPACK_MANAGER}/.cache"
  echo "Use the native Spack clean system":
  cmd "spack clean --all"
  echo "Cleaning out pycache from spack-manager repos:"
  cmd "find ${SPACK_MANAGER}/repos -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete"

printf "\nGenerating test script for submission...\n"
EXAWIND_TEST_SCRIPT=${SPACK_MANAGER}/scripts/exawind-tests-script.sh
cat > ${EXAWIND_TEST_SCRIPT} << '_EOF'
#!/bin/bash -l

# Trap and kill background processes
#trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

cmd() {
  echo "+ $@"
  eval "$@"
}

prep_gold_dirs() {
  cmd "rm -rf $1/tmp/amr-wind"
  cmd "mkdir -p $1/tmp/amr-wind"
  cmd "mkdir -p $1/archived/amr-wind"
  cmd "rm -rf $1/tmp/nalu-wind"
  cmd "mkdir -p $1/tmp/nalu-wind"
  cmd "mkdir -p $1/archived/nalu-wind"
}

archive_gold_dirs() {
  cmd "tar -czf $1/archived/amr-wind/amr-wind-golds-$2.tar.gz -C $1/tmp/amr-wind ."
  cmd "tar -czf $1/archived/nalu-wind/nalu-wind-golds-$2.tar.gz -C $1/tmp/nalu-wind ."
}

set -e

printf "Starting at $(date)\n"

printf "\nSetting up recommended environment for machine...\n"
ENV_SCRIPT=${SPACK_MANAGER}/configs/${SPACK_MANAGER_MACHINE}/env.sh
if [[ -f "${ENV_SCRIPT}" ]]; then
  cmd "source ${ENV_SCRIPT}"
fi

printf "\nSetting up gold files directories...\n"
if [[ "${SPACK_MANAGER_MACHINE}" == "cee" ]]; then
  prep_gold_dirs ${SPACK_MANAGER_GOLDS_DIR}-stable
  prep_gold_dirs ${SPACK_MANAGER_GOLDS_DIR}-develop
else
  prep_gold_dirs ${SPACK_MANAGER_GOLDS_DIR}
fi

printf "\nSetting up Spack environoment...\n"
cmd "export EXAWIND_ENV_DIR=${SPACK_MANAGER}/environments/exawind"
YAML_FILE="${SPACK_MANAGER}/env-templates/exawind_${SPACK_MANAGER_MACHINE}_tests.yaml"
cmd "spack manager create-env -y ${YAML_FILE} -d ${EXAWIND_ENV_DIR}"

printf "\nUpdating git repos in selected stage directories...\n"
cmd "spack env activate -d ${EXAWIND_ENV_DIR}"
#cmd "${SPACK_MANAGER}/scripts/stage-updater.py -e ${SPACK_MANAGER}/environments/exawind"
cmd "spack env deactivate"

printf "\nUninstall nightly test packages...\n"
cmd "spack uninstall -a -y exawind-nightly || true"
cmd "spack uninstall -a -y nalu-wind-nightly || true"
cmd "spack uninstall -a -y amr-wind-nightly || true"
cmd "spack uninstall --dependents -a -y trilinos || true"
cmd "spack uninstall --dependents -a -y hypre || true"

printf "\nActivating environment...\n"
cmd "spack env activate -d ${EXAWIND_ENV_DIR}"

printf "\nConcretizing environment...\n"
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

set +e
printf "\nTests started at: $(date)\n\n"
printf "spack install \n"
#if [ "${SPACK_MANAGER_MACHINE}" == 'cee' ]; then
time (spack install --keep-stage)
#else
#  time (for i in {1..2}; do spack install --keep-stage & done; wait)
#fi
printf "\nTests ended at: $(date)\n"
set -e

printf "\nSaving gold files...\n"
DATE=$(date +%Y-%m-%d-%H-%M)
if [[ "${SPACK_MANAGER_MACHINE}" == "cee" ]]; then
  archive_gold_dirs ${SPACK_MANAGER_GOLDS_DIR}-stable ${DATE}
  archive_gold_dirs ${SPACK_MANAGER_GOLDS_DIR}-develop ${DATE}
else
  archive_gold_dirs ${SPACK_MANAGER_GOLDS_DIR} ${DATE}
fi

#STAGE_DIR=$(spack location -S)
#if [ ! -z "${STAGE_DIR}" ]; then
#  #Haven't been able to find another robust way to rm with exclude
#  printf "\nRemoving all unused staged directories...\n"
#  cmd "cd ${STAGE_DIR} && rm -rf resource* spack-stage-b* spack-stage-c* spack-stage-d* spack-stage-f* spack-stage-g* spack-stage-h* spack-stage-i* spack-stage-j* spack-stage-k* spack-stage-l* spack-stage-m* spack-stage-nc* spack-stage-net* spack-stage-o* spack-stage-p* spack-stage-q* spack-stage-r* spack-stage-s* spack-stage-tar* spack-stage-ti* spack-stage-u* spack-stage-v* spack-stage-w* spack-stage-x* spack-stage-y* spack-stage-z*"
#  #Would like something like this
#  #find ${STAGE_DIR}/ -maxdepth 0 -type d -not -name "spack-stage-trilinos*" -exec rm -r {} \;
#fi

printf "\nDeactivating environment...\n"
cmd "spack env deactivate"

printf "\nDone at $(date)\n"
_EOF

cmd "chmod u+x ${EXAWIND_TEST_SCRIPT}"

printf "\nRunning test script...\n"
LOG_DIR=${SPACK_MANAGER}/logs
mkdir -p ${LOG_DIR}
DATE=$(date +%Y-%m-%d)
if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
  (set -x; cd ${LOG_DIR} && sbatch -J test-exawind-${DATE} -N 1 -t 4:00:00 -A exawind -p short -o "%x.o%j" --gres=gpu:2 ${EXAWIND_TEST_SCRIPT})
elif [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
  (set -x; cd ${LOG_DIR} && nice -n20 ${EXAWIND_TEST_SCRIPT} &> test-exawind-${DATE}.log)
else
  (set -x; cd ${LOG_DIR} && nice -n19 ionice -c3 ${EXAWIND_TEST_SCRIPT} &> test-exawind-${DATE}.log)
fi

printf "\nDone at $(date)\n"
