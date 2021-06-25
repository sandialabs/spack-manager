#!/bin/bash

cmd() {
  echo "+ $@"
  eval "$@"
}

test_configuration() {
  printf "************************************************************\n"
  printf "Testing AMR-Wind with:\n"
  printf "${CONFIGURATION}\n"
  printf "at $(date)\n"
  printf "************************************************************\n"
  printf "\n"

  SPEC="amr-wind-nightly ${CONFIGURATION} host_name=${HOST_NAME}"
  cmd "sspack install --keep-stage ${SPEC}"

  printf "\nDeleting gold files older than 30 days...\n"
  cmd "cd ${GOLDS_DIR} && find . -mtime +30 -not -path '*/\.*' -delete"
  printf "\n"

  # Here we create a CMake project on the fly to have it write its OS/compiler info to a file
  printf "Organizing gold files from multiple tests into a single directory...\n"
  if [ ! -z "${SPACK_MANAGER}/tmp/id" ]; then
    cmd "mkdir -p ${SPACK_MANAGER}/tmp/id/build"
  fi
  printf "\nWriting CMake ID project CMakeLists.txt...\n"
  ID_CMAKE_LISTS=${SPACK_MANAGER}/tmp/id/CMakeLists.txt
  cat >${ID_CMAKE_LISTS} <<'EOL'
cmake_minimum_required(VERSION 3.11)
project(ID CXX)
file(WRITE ${CMAKE_BINARY_DIR}/id.txt ${CMAKE_SYSTEM_NAME}/${CMAKE_CXX_COMPILER_ID}/${CMAKE_CXX_COMPILER_VERSION})
EOL
  printf "\nRunning CMake on ID project...\n"
  unset CMAKE_CXX
  if [ "${COMPILER_NAME}" == 'intel' ]; then
    CMAKE_CXX="CXX=icpc"
  fi
  cmd "cd ${SPACK_MANAGER}/tmp/id/build && ${CMAKE_CXX} cmake .."
  ID_FILE=$(cat ${SPACK_MANAGER}/tmp/id/build/id.txt)

  printf "\nID_FILE contains: ${ID_FILE}\n"

  if [ ! -z "${SPACK_MANAGER}/tmp/id" ]; then
    cmd "rm -rf ${SPACK_MANAGER}/tmp/id"
  fi

  printf "\nCopying fcompare golds to organized directory...\n"
  cmd "mkdir -p ${TMP_GOLDS_DIR}/${ID_FILE}"
  (set -x; rsync -avm --include="*/" --include="plt00010**" --exclude="*" $(sspack location -b ${SPEC})/test/test_files/ ${TMP_GOLDS_DIR}/${ID_FILE}/)

  printf "\n"
  printf "************************************************************\n"
  printf "Done testing AMR-Wind with:\n"
  printf "${CONFIGURATION}\n"
  printf "at $(date)\n"
  printf "************************************************************\n"
}

# Main function for assembling configurations to test
main() {
  printf "============================================================\n"
  printf "$(date)\n"
  printf "============================================================\n"
  printf "Job is running on ${HOSTNAME}\n"
  printf "============================================================\n"

  # Needed to get sspack
  source ${SPACK_MANAGER}/start.sh

  if [ "${SPACK_MANAGER_MACHINE}" == 'rhodes' ] ||
     [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ] ||
     [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
    HOST_NAME="${SPACK_MANAGER_MACHINE}.hpc.nrel.gov"
  elif [ "${SPACK_MANAGER_MACHINE}" == 'skybridge' ] ||
       [ "${SPACK_MANAGER_MACHINE}" == 'ascicgpu' ]; then
    HOST_NAME="${SPACK_MANAGER_MACHINE}.snl.gov"
  fi
 
  # Set configurations to test for each machine
  declare -a CONFIGURATIONS
  if [ "${SPACK_MANAGER_MACHINE}" == 'rhodes' ]; then
    CONFIGURATIONS[0]='+netcdf+hypre+openfast~latest_amrex%intel@18.0.4'
    CONFIGURATIONS[1]='+netcdf+hypre+openfast~latest_amrex%clang@10.0.0'
    CONFIGURATIONS[2]='+netcdf+hypre+openfast+latest_amrex%gcc@8.4.0'
    CONFIGURATIONS[3]='+netcdf+hypre+openfast~latest_amrex%gcc@8.4.0'
  elif [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
    CONFIGURATIONS[0]='+netcdf+hypre+openfast+latest_amrex%gcc@8.4.0'
    CONFIGURATIONS[1]='+netcdf+hypre+openfast~latest_amrex%gcc@8.4.0'
  elif [ "${SPACK_MANAGER_MACHINE}" == 'darwin' ]; then
    CONFIGURATIONS[0]='+netcdf+hypre+openfast~latest_amrex%apple-clang@12.0.0'
  else
    printf "\nTesting machine not recognized.\n"
    exit 1
  fi
 
  LOGS_DIR=${SPACK_MANAGER}/logs
  GOLDS_DIR=${SPACK_MANAGER}/golds
  TMP_GOLDS_DIR=${SPACK_MANAGER}/tmp/amr_wind_temp_golds
 
  printf "============================================================\n"
  printf "HOST_NAME: ${HOST_NAME}\n"
  printf "Testing configurations:\n"
  for CONFIGURATION in "${CONFIGURATIONS[@]}"; do
    printf " ${CONFIGURATION}\n"
  done
  printf "============================================================\n"

  printf "\nMaking common directory across all tests in which to organize and save gold files...\n"
  if [ ! -z "${TMP_GOLDS_DIR}" ]; then
    cmd "mkdir -p ${TMP_GOLDS_DIR}"
  fi

  printf "\n"
  printf "============================================================\n"
  printf "Starting testing loops...\n"
  printf "============================================================\n"
 
  # Test AMR-Wind for the list of configurations
  for CONFIGURATION in "${CONFIGURATIONS[@]}"; do
    printf "\nRemoving previous test log for uploading to CDash...\n"
    cmd "rm -f ${LOGS_DIR}/amr-wind-test-log.txt"
    printf "\n"
    (test_configuration) 2>&1 | tee -i ${LOGS_DIR}/amr-wind-test-log.txt
  done

  printf "============================================================\n"
  printf "Done with testing loops\n"
  printf "============================================================\n"
  printf "============================================================\n"
  printf "Final steps\n"
  printf "============================================================\n"

  printf "\nSaving gold files...\n"
  (set -x; tar -czf ${GOLDS_DIR}/amr_wind_golds-$(date +%Y-%m-%d-%H-%M).tar.gz -C ${TMP_GOLDS_DIR} .)

  printf "\nRemoving temporary golds...\n"
  if [ ! -z "${TMP_GOLDS_DIR}" ]; then
    cmd "rm -rf ${TMP_GOLDS_DIR}"
  fi

  printf "============================================================\n"
  printf "Done!\n"
  printf "$(date)\n"
  printf "============================================================\n"
}

main "$@"
