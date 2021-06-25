#!/bin/bash -l

cmd() {
  echo "+ $@"
  eval "$@"
}

test_configuration() {
  COMPILER_ID="${COMPILER_NAME}@${COMPILER_VERSION}"
  printf "************************************************************\n"
  printf "Testing AMR-Wind with:\n"
  printf "${COMPILER_ID}\n"
  printf "LIST_OF_TPLS: ${LIST_OF_TPLS}\n"
  printf "at $(date)\n"
  printf "************************************************************\n"
  printf "\n"

  #CUDA version used for tests on Eagle
  CUDA_VERSION="10.2.89"

  cmd "cd ${AMR_WIND_TESTING_ROOT_DIR}"

  # Run static analysis and let ctest know we have static analysis output
  if [ "${MACHINE_NAME}" == 'rhodes' ] && [ "${COMPILER_ID}" == 'clang@10.0.0' ]; then
    cmd "cd ${AMR_WIND_DIR}/build && ln -s ${CPPCHECK_ROOT_DIR}/cfg/std.cfg"
    cmd "rm ${LOGS_DIR}/amr-wind-static-analysis.txt || true"
    printf "\nRunning cppcheck static analysis (AMR-Wind not updated until after this step)...\n"
    # Using a working directory for cppcheck makes analysis faster
    cmd "mkdir cppcheck-wd"
    # Cppcheck ignores -isystem directories, so we change them to regular -I include directories (with no spaces either)
    cmd "sed -i 's/isystem /I/g' compile_commands.json"
    cmd "cppcheck --template=gcc --inline-suppr --suppress=danglingTemporaryLifetime --suppress=unreadVariable --suppress=internalAstError --suppress=unusedFunction --suppress=unmatchedSuppression --std=c++14 --language=c++ --enable=all --project=compile_commands.json -j 32 --cppcheck-build-dir=cppcheck-wd -i ${AMR_WIND_DIR}/submods/amrex/Src -i ${AMR_WIND_DIR}/submods/googletest --output-file=cppcheck.txt"
    # Warnings in header files are unavoidable, so we filter out submodule headers after analysis
    cmd "awk -v nlines=2 '/submods\/amrex/ || /submods\/googletest/ {for (i=0; i<nlines; i++) {getline}; next} 1' < cppcheck.txt > cppcheck-warnings.txt"
    (set -x; cat cppcheck-warnings.txt | egrep 'information:|error:|performance:|portability:|style:|warning:' | sort | awk 'BEGIN{i=0}{print $0}{i++}END{print "Warnings: "i}' > ${LOGS_DIR}/amr-wind-static-analysis.txt)
    CTEST_ARGS="-DHAVE_STATIC_ANALYSIS_OUTPUT:BOOL=TRUE -DSTATIC_ANALYSIS_LOG=${LOGS_DIR}/amr-wind-static-analysis.txt ${CTEST_ARGS}"
  fi

  if [ ! -z "${AMR_WIND_DIR}" ]; then
    printf "\nCleaning AMR-Wind directory...\n"
    cmd "cd ${AMR_WIND_DIR} && git reset --hard origin/main && git clean -df && git status -uno"
    cmd "cd ${AMR_WIND_DIR}/submods/amrex && git reset --hard origin/development && git clean -df && git status -uno"
    cmd "mkdir -p ${AMR_WIND_DIR}/build || true"
    cmd "cd ${AMR_WIND_DIR}/build && rm -rf ${AMR_WIND_DIR}/build/*"
    # Update all the submodules recursively in case the previous ctest update failed because of submodule updates
    cmd "cd ${AMR_WIND_DIR} && git submodule update --init --recursive"
    cmd "ln -sfn ${HOME}/exawind/AMR-WindGoldFiles ${AMR_WIND_DIR}/test/AMR-WindGoldFiles"
    if [ "${USE_LATEST_AMREX}" == 'true' ]; then
      CTEST_ARGS="-DUSE_LATEST_AMREX:BOOL=TRUE ${CTEST_ARGS}"
      EXTRA_BUILD_NAME="${EXTRA_BUILD_NAME}-amrex_dev"
    fi
  fi

  printf "\nRunning testing at $(date)...\n"
  cmd "spack install amr-wind"
  printf "Returned from testing at $(date)\n"

  printf "\nGoing to delete these gold files older than 30 days:\n"
  cmd "cd ${GOLDS_DIR} && find . -mtime +30 -not -path '*/\.*'"
  printf "\nDeleting the files...\n"
  cmd "cd ${GOLDS_DIR} && find . -mtime +30 -not -path '*/\.*' -delete"
  printf "\n"

  # Here we create a CMake project on the fly to have it write its OS/compiler info to a file
  printf "Organizing gold files from multiple tests into a single directory...\n"
  if [ ! -z "${AMR_WIND_DIR}" ]; then
    cmd "mkdir -p ${AMR_WIND_DIR}/build/id/build"
  fi
  printf "\nWriting CMake ID project CMakeLists.txt...\n"
  ID_CMAKE_LISTS=${AMR_WIND_DIR}/build/id/CMakeLists.txt
  cat >${ID_CMAKE_LISTS} <<'EOL'
cmake_minimum_required(VERSION 3.11)
project(ID CXX)
file(WRITE ${CMAKE_BINARY_DIR}/id.txt ${CMAKE_SYSTEM_NAME}/${CMAKE_CXX_COMPILER_ID}/${CMAKE_CXX_COMPILER_VERSION})
EOL
  printf "\nRunning CMake on ID project...\n"
  unset CMAKE_CXX
  if [ "${MACHINE_NAME}" == 'mac' ] && [ "${COMPILER_NAME}" == 'gcc' ]; then
    CMAKE_CXX="CXX=g++-7"
  elif [ "${COMPILER_NAME}" == 'intel' ]; then
    CMAKE_CXX="CXX=icpc"
  fi
  cmd "cd ${AMR_WIND_DIR}/build/id/build && ${CMAKE_CXX} cmake .."
  ID_FILE=$(cat ${AMR_WIND_DIR}/build/id/build/id.txt)

  printf "\nID_FILE contains: ${ID_FILE}\n"

  printf "\nCopying fcompare golds to organized directory...\n"
  cmd "mkdir -p ${AMR_WIND_TESTING_ROOT_DIR}/temp_golds/${ID_FILE}"
  (set -x; rsync -avm --include="*/" --include="plt00010**" --exclude="*" ${AMR_WIND_DIR}/build/test/test_files/ ${AMR_WIND_TESTING_ROOT_DIR}/temp_golds/${ID_FILE}/)

  printf "\n"
  printf "************************************************************\n"
  printf "Done testing AMR-Wind with:\n"
  printf "${COMPILER_ID}\n"
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

  # Decide what machine we are on
  if [ "${NREL_CLUSTER}" == 'eagle' ]; then
    MACHINE_NAME=eagle
  elif [ $(hostname) == 'rhodes.hpc.nrel.gov' ]; then
    MACHINE_NAME=rhodes
  elif [ $(hostname) == 'jrood-31712s.nrel.gov' ]; then
    MACHINE_NAME=mac
  fi
    
  HOST_NAME="${MACHINE_NAME}.hpc.nrel.gov"
 
  # Set configurations to test for each machine
  declare -a CONFIGURATIONS
  #CONFIGURATION[n]='compiler_name:compiler_version:use_latest_amrex'
  if [ "${MACHINE_NAME}" == 'rhodes' ]; then
    CONFIGURATIONS[0]='intel:18.0.4:false:netcdf;hypre;openfast'
    CONFIGURATIONS[1]='clang:10.0.0:false:netcdf;hypre;openfast;masa'
    CONFIGURATIONS[2]='gcc:8.4.0:true:netcdf;hypre;openfast;masa'
    CONFIGURATIONS[3]='gcc:8.4.0:false:netcdf;hypre;openfast;masa'
    NALU_WIND_TESTING_ROOT_DIR=/projects/ecp/exawind/nalu-wind-testing
    INTEL_COMPILER_MODULE=intel-parallel-studio/cluster.2018.4
  elif [ "${MACHINE_NAME}" == 'eagle' ]; then
    CONFIGURATIONS[0]='gcc:8.4.0:true:netcdf;hypre;openfast'
    CONFIGURATIONS[1]='gcc:8.4.0:false:netcdf;hypre;openfast'
    NALU_WIND_TESTING_ROOT_DIR=/projects/hfm/exawind/nalu-wind-testing
    INTEL_COMPILER_MODULE=intel-parallel-studio/cluster.2018.4
  elif [ "${MACHINE_NAME}" == 'mac' ]; then
    CONFIGURATIONS[0]='apple-clang:12.0.0-apple:false'
    NALU_WIND_TESTING_ROOT_DIR=${HOME}/nalu-wind-testing
  else
    printf "\nMachine name not recognized.\n"
    exit 1
  fi
 
  AMR_WIND_TESTING_ROOT_DIR=${NALU_WIND_TESTING_ROOT_DIR}/amr-wind-testing
  AMR_WIND_DIR=${AMR_WIND_TESTING_ROOT_DIR}/amr-wind
  BUILD_TEST_DIR=${NALU_WIND_TESTING_ROOT_DIR}/build-test
  LOGS_DIR=${NALU_WIND_TESTING_ROOT_DIR}/logs
  GOLDS_DIR=${AMR_WIND_TESTING_ROOT_DIR}/golds
  cmd "export SPACK_ROOT=${NALU_WIND_TESTING_ROOT_DIR}/spack"
 
  printf "============================================================\n"
  printf "HOST_NAME: ${HOST_NAME}\n"
  printf "AMR_WIND_TESTING_ROOT_DIR: ${AMR_WIND_TESTING_ROOT_DIR}\n"
  printf "AMR_WIND_DIR: ${AMR_WIND_DIR}\n"
  printf "BUILD_TEST_DIR: ${BUILD_TEST_DIR}\n"
  printf "LOGS_DIR: ${LOGS_DIR}\n"
  printf "GOLDS_DIR: ${GOLDS_DIR}\n"
  printf "SPACK_ROOT: ${SPACK_ROOT}\n"
  printf "Testing configurations:\n"
  printf " compiler_name:compiler_version:use_latest_amrex\n"
  for CONFIGURATION in "${CONFIGURATIONS[@]}"; do
    printf " ${CONFIGURATION}\n"
  done
  printf "============================================================\n"
 
  if [ ! -d "${AMR_WIND_TESTING_ROOT_DIR}" ]; then
    set -e
    printf "============================================================\n"
    printf "Top level testing directory doesn't exist.\n"
    printf "Creating everything from scratch...\n"
    printf "============================================================\n"

    printf "Creating top level testing directory...\n"
    cmd "mkdir -p ${AMR_WIND_TESTING_ROOT_DIR}"
 
    #printf "\nCloning Spack repo...\n"
    #cmd "git clone https://github.com/spack/spack.git ${SPACK_ROOT}"
 
    #printf "\nConfiguring Spack...\n"
    #cmd "git clone https://github.com/exawind/build-test.git ${BUILD_TEST_DIR}"
    #cmd "cd ${BUILD_TEST_DIR}/configs && ./setup-spack.sh"
 
    printf "\nCloning AMR-Wind repo...\n"
    cmd "git clone --recursive -b main https://github.com/Exawind/amr-wind.git ${AMR_WIND_DIR}"
    cmd "mkdir -p ${AMR_WIND_DIR}/build || true"

    #printf "\nMaking job output directory...\n"
    #cmd "mkdir -p ${LOGS_DIR}"

    printf "\nMaking golds archive directory...\n"
    cmd "mkdir -p ${GOLDS_DIR}"
 
    printf "============================================================\n"
    printf "Done setting up testing directory\n"
    printf "============================================================\n"
    set +e
  fi
 
  printf "\nLoading Spack...\n"
  cmd "source ${SPACK_ROOT}/share/spack/setup-env.sh"

  printf "\nMaking common directory across all tests in which to organize and save gold files...\n"
  if [ ! -z "${AMR_WIND_TESTING_ROOT_DIR}" ]; then
    cmd "mkdir -p ${AMR_WIND_TESTING_ROOT_DIR}/temp_golds"
  fi

  printf "\n"
  printf "============================================================\n"
  printf "Starting testing loops...\n"
  printf "============================================================\n"
 
  # Test AMR-Wind for the list of configurations
  for CONFIGURATION in "${CONFIGURATIONS[@]}"; do
    CONFIG=(${CONFIGURATION//:/ })
    COMPILER_NAME=${CONFIG[0]}
    COMPILER_VERSION=${CONFIG[1]}
    USE_LATEST_AMREX=${CONFIG[2]}
    LIST_OF_TPLS=${CONFIG[3]}

    printf "\nRemoving previous test log for uploading to CDash...\n"
    cmd "rm ${LOGS_DIR}/amr-wind-test-log.txt"
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
  (set -x; tar -czf ${GOLDS_DIR}/amr_wind_golds-$(date +%Y-%m-%d-%H-%M).tar.gz -C ${AMR_WIND_TESTING_ROOT_DIR}/temp_golds .)

  printf "\nRemoving temporary golds...\n"
  if [ ! -z "${AMR_WIND_TESTING_ROOT_DIR}" ]; then
    cmd "rm -rf ${AMR_WIND_TESTING_ROOT_DIR}/temp_golds"
  fi

  if [ "${MACHINE_NAME}" == 'eagle' ] || [ "${MACHINE_NAME}" == 'rhodes' ]; then
    printf "\nSetting permissions...\n"
    cmd "chmod -R a+rX,go-w ${AMR_WIND_TESTING_ROOT_DIR}"
  fi

  if [ "${MACHINE_NAME}" == 'rhodes' ]; then
    printf "\nSetting group...\n"
    cmd "chgrp -R windsim ${AMR_WIND_TESTING_ROOT_DIR}"
  fi

  printf "============================================================\n"
  printf "Done!\n"
  printf "$(date)\n"
  printf "============================================================\n"
}

main "$@"
