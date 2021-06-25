#!/bin/bash -l

# Script for running nightly regression tests for Nalu-Wind on a particular set 
# of machines with a list of configurations for each machine using Spack
# to satisfy dependencies and submitting results to CDash

# Function for printing and executing commands
cmd() {
  echo "+ $@"
  eval "$@"
}

# Function for testing a single configuration
test_configuration() {
  COMPILER_ID="${COMPILER_NAME}@${COMPILER_VERSION}"
  printf "************************************************************\n"
  printf "Testing Nalu-Wind with:\n"
  printf "${COMPILER_ID}\n"
  printf "trilinos@${TRILINOS_BRANCH}\n"
  printf "LIST_OF_TPLS: ${LIST_OF_TPLS}\n"
  printf "at $(date)\n"
  printf "************************************************************\n"
  printf "\n"

  # Logic for building up some constraints for use on Spack commands
  GENERAL_CONSTRAINTS=''
  MPI_ID=''
  MPI_CONSTRAINTS=''
  BLAS_ID=''
  BLAS_CONSTRAINTS=''
  if [ "${COMPILER_NAME}" == 'gcc' ] || [ "${COMPILER_NAME}" == 'clang' ]; then
    MPI_ID="openmpi"
  elif [ "${COMPILER_NAME}" == 'intel' ]; then
    # For intel, we want to build against intel-mpi and intel-mkl
    MPI_ID="intel-mpi"
    BLAS_ID="intel-mkl"
  fi
  if [ "${MACHINE_NAME}" == 'eagle' ]; then
    MPI_ID="mpt@2.22"
  fi
  if [ ! -z "${MPI_ID}" ]; then
    # Avoid listing plain openmpi without a version number
    if [ "${MPI_ID}" == 'openmpi' ]; then
      MPI_CONSTRAINTS=''
    else
      MPI_CONSTRAINTS="^${MPI_ID}"
    fi
  fi
  if [ ! -z "${BLAS_ID}" ]; then
    BLAS_CONSTRAINTS=" ^${BLAS_ID}"
  fi
  GENERAL_CONSTRAINTS="${MPI_CONSTRAINTS}${BLAS_CONSTRAINTS}"
  printf "Using constraints: ${GENERAL_CONSTRAINTS}\n\n"

  TRILINOS="trilinos"

  #CUDA version used for tests on Eagle
  CUDA_VERSION="10.2.89"

  cmd "cd ${NALU_WIND_TESTING_ROOT_DIR}"

  printf "\nLoading modules...\n"
  if [ "${MACHINE_NAME}" == 'rhodes' ]; then
    cmd "module purge"
    cmd "module unuse ${MODULEPATH}"
    cmd "module use /opt/compilers/modules-2020-07"
    cmd "module use /opt/utilities/modules-2020-07"
    cmd "module load unzip"
    cmd "module load patch"
    cmd "module load bzip2"
    cmd "module load git"
    cmd "module load flex"
    cmd "module load bison"
    cmd "module load wget"
    cmd "module load bc"
    cmd "module load python"
    cmd "module load cppcheck"
    cmd "module load binutils"
    if [ "${COMPILER_NAME}" == 'gcc' ]; then
      cmd "module load ${COMPILER_NAME}/${COMPILER_VERSION}"
    elif [ "${COMPILER_NAME}" == 'clang' ]; then
      cmd "module load llvm/${COMPILER_VERSION}"
    elif [ "${COMPILER_NAME}" == 'intel' ]; then
      cmd "module load gcc"
      cmd "module load ${INTEL_COMPILER_MODULE}"
    fi
  elif [ "${MACHINE_NAME}" == 'eagle' ]; then
    cmd "module purge"
    cmd "module unuse ${MODULEPATH}"
    cmd "module use /nopt/nrel/ecom/hpacf/compilers/modules-2020-07"
    cmd "module use /nopt/nrel/ecom/hpacf/utilities/modules-2020-07"
    cmd "module use /nopt/nrel/ecom/hpacf/software/modules-2020-07/gcc-8.4.0"
    cmd "module load python"
    cmd "module load git"
    cmd "module load binutils"
    cmd "module load cuda/${CUDA_VERSION}"
    if [ "${COMPILER_NAME}" == 'gcc' ]; then
      cmd "module load ${COMPILER_NAME}/${COMPILER_VERSION}"
    elif [ "${COMPILER_NAME}" == 'intel' ]; then
      cmd "module load gcc"
      cmd "module load ${INTEL_COMPILER_MODULE}"
    fi
  fi

  if [ "${MACHINE_NAME}" == 'mac' ] || [ "${MACHINE_NAME}" == 'eagle' ]; then
    printf "\nDisabling shared build in Trilinos because we're testing with CUDA or are on a Mac...\n"
    TRILINOS="${TRILINOS}~shared"
  fi

  # Set the TMPDIR to disk so it doesn't run out of space
  if [ "${MACHINE_NAME}" == 'eagle' ]; then
    printf "\nMaking and setting TMPDIR to disk...\n"
    cmd "mkdir -p /scratch/${USER}/.tmp"
    cmd "export TMPDIR=/scratch/${USER}/.tmp"
  fi

  # Store hash from Trilinos before it's uninstalled
  INSTALLED_TRILINOS_HASH=$(spack --color never find -L trilinos@${TRILINOS_BRANCH} %${COMPILER_ID} | grep trilinos | cut -d " " -f1)
  printf "\nINSTALLED_TRILINOS_HASH=${INSTALLED_TRILINOS_HASH}\n"
  TRILINOS_INSTALL_DIR=$(spack location -i trilinos@${TRILINOS_BRANCH} %${COMPILER_ID})
  printf "\nTRILINOS_INSTALL_DIR=${TRILINOS_INSTALL_DIR}\n"
  TRILINOS_BASENAME=$(basename ${TRILINOS_INSTALL_DIR})
  printf "\nTRILINOS_BASENAME=${TRILINOS_BASENAME}\n"
  TRILINOS_STAGE_DIR=$(spack location -S)/spack-stage-${TRILINOS_BASENAME}
  printf "\nTRILINOS_STAGE_DIR=${TRILINOS_STAGE_DIR}\n"

  # Uninstall packages we want to track; it's an error if they don't exist yet, but a soft error
  printf "\nUninstalling Trilinos (this is fine to error when tests are first run or building Trilinos has previously failed)...\n"
  cmd "spack uninstall -a -y trilinos@${TRILINOS_BRANCH} %${COMPILER_ID} || true"
  #printf "\nUninstalling OpenFAST (this is fine to error when tests are first run or building OpenFAST has previously failed)...\n"
  #cmd "spack uninstall -a -y openfast %${COMPILER_ID} || true"
  #printf "\nUninstalling TIOGA (this is fine to error when tests are first run or building TIOGA has previously failed)...\n"
  #cmd "spack uninstall -a -y tioga %${COMPILER_ID} || true"
  printf "\nUninstalling hypre...\n"
  cmd "spack uninstall -a -y hypre %${COMPILER_ID} || true"

  # Update packages we want to track; it's an error if they don't exist yet, but a soft error
  printf "\nUpdating and cleaning Trilinos stage directory (this is fine to error when tests are first run)...\n"
  cmd "cd ${TRILINOS_STAGE_DIR}/spack-src && pwd && git fetch --all && git reset --hard origin/${TRILINOS_BRANCH} && git clean -df && git status -uno && rm -rf ../spack-build ../spack-build.out ../spack-build.env || true"
  # Update Trilinos using the hash from the previous install
  #cmd "spack cd /${INSTALLED_TRILINOS_HASH} && pwd && git fetch --all && git reset --hard origin/${TRILINOS_BRANCH} && git clean -df && git status -uno && rm -rf ../spack-build ../spack-build.out ../spack-build.env || true"
  # Update Trilinos using spack cd
  #cmd "spack cd ${TRILINOS}@${TRILINOS_BRANCH} %${COMPILER_ID} ${GENERAL_CONSTRAINTS} && pwd && git fetch --all && git reset --hard origin/${TRILINOS_BRANCH} && git clean -df && git status -uno && rm -rf ../spack-build ../spack-build.out ../spack-build.env || true"

  cmd "cd ${NALU_WIND_TESTING_ROOT_DIR}" # Change directories to avoid any stale file handles

  TPL_VARIANTS=''
  TPL_CONSTRAINTS=''
  TPLS=(${LIST_OF_TPLS//;/ })
  for TPL in ${TPLS[*]}; do
    TPL_VARIANTS+="+${TPL}"
    # Currently don't need any extra constraints for openfast
    #if [ "${TPL}" == 'openfast' ] ; then
    #  TPL_CONSTRAINTS="^openfast@develop ${TPL_CONSTRAINTS}"
    #fi
    # Currently don't need any extra constraints for tioga
    #if [ "${TPL}" == 'tioga' ] ; then
    #  TPL_CONSTRAINTS="^tioga@master ${TPL_CONSTRAINTS}"
    #fi
    # Currently don't need any extra constraints for catalyst
    #if [ "${TPL}" == 'catalyst' ] ; then
    #  TPL_CONSTRAINTS="${TPL_CONSTRAINTS}"
    #fi
    # Currently don't need any extra constraints for hypre
    #if [ "${TPL}" == 'hypre' ] ; then
    #  TPL_CONSTRAINTS="${TPL_CONSTRAINTS}"
    #fi
    # Currently don't need any extra constraints for fftw
    #if [ "${TPL}" == 'fftw' ] ; then
    #  TPL_CONSTRAINTS="${TPL_CONSTRAINTS}"
    #fi
    if [ "${TPL}" == 'cuda' ] ; then
      TPL_VARIANTS+="~shared cuda_arch=70 "
    fi
  done

  if [ "${MACHINE_NAME}" != 'mac' ]; then
    cmd "module list"
  fi

  printf "\nInstalling Nalu-Wind dependencies using ${COMPILER_ID}...\n"
  cmd "spack install --dont-restage --keep-stage --only dependencies nalu-wind ${TPL_VARIANTS} %${COMPILER_ID} ^${TRILINOS}@${TRILINOS_BRANCH} ${TPL_CONSTRAINTS} ${GENERAL_CONSTRAINTS}"

  STAGE_DIR=$(spack location -S)
  if [ ! -z "${STAGE_DIR}" ]; then
    #Haven't been able to find another robust way to rm with exclude
    printf "\nRemoving all staged directories except Trilinos...\n"
    cmd "cd ${STAGE_DIR} && rm -rf spack-stage-a* spack-stage-b* spack-stage-c* spack-stage-d* spack-stage-e* spack-stage-f* spack-stage-g* spack-stage-h* spack-stage-i* spack-stage-j* spack-stage-k* spack-stage-l* spack-stage-m* spack-stage-n* spack-stage-o* spack-stage-p* spack-stage-q* spack-stage-r* spack-stage-s* spack-stage-tar* spack-stage-u* spack-stage-v* spack-stage-w* spack-stage-x* spack-stage-y* spack-stage-z*"
    #printf "\nRemoving all staged directories except Trilinos and OpenFAST...\n"
    #cmd "cd ${STAGE_DIR} && rm -rf a* b* c* d* e* f* g* h* i* j* k* l* m* n* openmpi* p* q* r* s* tar* u* v* w* x* y* z*"
    #find ${STAGE_DIR}/ -maxdepth 0 -type d -not -name "trilinos*" -exec rm -r {} \;
  fi

  # Refresh available modules (this is only really necessary on the first run of this script
  # because cmake and openmpi will already have been built and module files registered in subsequent runs)
  cmd "source ${SPACK_ROOT}/share/spack/setup-env.sh"

  printf "\nLoading Spack modules into environment for CMake and MPI to use during CTest...\n"
  if [ "${MACHINE_NAME}" == 'mac' ]; then
    cmd "export PATH=$(spack location -i cmake %${COMPILER_ID})/bin:${PATH}"
    cmd "export PATH=$(spack location -i nccmp %${COMPILER_ID})/bin:${PATH}"
    cmd "export PATH=$(spack location -i ${MPI_ID} %${COMPILER_ID})/bin:${PATH}"
  elif [ "${MACHINE_NAME}" == 'eagle' ]; then
    cmd "spack load cmake %${COMPILER_ID}"
    cmd "spack load nccmp %${COMPILER_ID}"
    cmd "spack load ${MPI_ID} %${COMPILER_ID}"
  else
    cmd "spack load cmake %${COMPILER_ID}"
    cmd "spack load nccmp %${COMPILER_ID}"
    cmd "spack load ${MPI_ID} %${COMPILER_ID}"
  fi

  printf "\nSetting variables to pass to CTest...\n"
  TRILINOS_DIR=$(spack location -i trilinos@${TRILINOS_BRANCH} %${COMPILER_ID})
  YAML_DIR=$(spack location -i yaml-cpp %${COMPILER_ID})
  printf "TRILINOS_DIR=${TRILINOS_DIR}\n"
  printf "YAML_DIR=${YAML_DIR}\n"
  CMAKE_CONFIGURE_ARGS=''
  for TPL in ${TPLS[*]}; do
    if [ "${TPL}" == 'openfast' ]; then
      OPENFAST_DIR=$(spack location -i openfast %${COMPILER_ID})
      CMAKE_CONFIGURE_ARGS="-DENABLE_OPENFAST:BOOL=ON -DOpenFAST_DIR:PATH=${OPENFAST_DIR} ${CMAKE_CONFIGURE_ARGS}"
      printf "OPENFAST_DIR=${OPENFAST_DIR}\n"
    fi
    if [ "${TPL}" == 'tioga' ]; then
      TIOGA_DIR=$(spack location -i tioga %${COMPILER_ID})
      CMAKE_CONFIGURE_ARGS="-DENABLE_TIOGA:BOOL=ON -DTIOGA_DIR:PATH=${TIOGA_DIR} ${CMAKE_CONFIGURE_ARGS}"
      printf "TIOGA_DIR=${TIOGA_DIR}\n"
    fi
    if [ "${TPL}" == 'catalyst' ]; then
      cmd "spack load paraview %${COMPILER_ID}"
      cmd "spack load trilinos-catalyst-ioss-adapter %${COMPILER_ID}"
      cmd "spack load py-numpy %${COMPILER_ID}"
      CATALYST_ADAPTER_DIR=$(spack location -i trilinos-catalyst-ioss-adapter %${COMPILER_ID})
      CMAKE_CONFIGURE_ARGS="-DENABLE_PARAVIEW_CATALYST:BOOL=ON -DPARAVIEW_CATALYST_INSTALL_PATH:PATH=${CATALYST_ADAPTER_DIR} ${CMAKE_CONFIGURE_ARGS}"
      printf "CATALYST_ADAPTER_DIR=${CATALYST_ADAPTER_DIR}\n"
    fi
    if [ "${TPL}" == 'hypre' ]; then
      if [ "${MACHINE_NAME}" == 'eagle' ]; then
        HYPRE_DIR=$(spack location -i hypre~shared %${COMPILER_ID})
      else
        HYPRE_DIR=$(spack location -i hypre %${COMPILER_ID})
      fi
      CMAKE_CONFIGURE_ARGS="-DENABLE_HYPRE:BOOL=ON -DHYPRE_DIR:PATH=${HYPRE_DIR} ${CMAKE_CONFIGURE_ARGS}"
      printf "HYPRE_DIR=${HYPRE_DIR}\n"
    fi
    if [ "${TPL}" == 'fftw' ]; then
      FFTW_DIR=$(spack location -i fftw %${COMPILER_ID})
      CMAKE_CONFIGURE_ARGS="-DENABLE_FFTW:BOOL=ON -DFFTW_DIR:PATH=${FFTW_DIR} ${CMAKE_CONFIGURE_ARGS}"
      printf "FFTW_DIR=${FFTW_DIR}\n"
    fi
    if [ "${TPL}" == 'cuda' ]; then
      CMAKE_CONFIGURE_ARGS="-DENABLE_CUDA:BOOL=ON ${CMAKE_CONFIGURE_ARGS}"
    fi
  done

  # Set the extra identifiers for CDash build description
  EXTRA_BUILD_NAME="-${COMPILER_NAME}-${COMPILER_VERSION}-tr_${TRILINOS_BRANCH}"

  if [ ! -z "${NALU_WIND_DIR}" ]; then
    printf "\nCleaning Nalu-Wind directory...\n"
    cmd "cd ${NALU_WIND_DIR} && git reset --hard origin/master && git clean -df && git status -uno"
    cmd "cd ${NALU_WIND_DIR}/build && rm -rf ${NALU_WIND_DIR}/build/*"
    # Update all the submodules recursively in case the previous ctest update failed because of submodule updates
    cmd "cd ${NALU_WIND_DIR} && git submodule update --init --recursive"
  fi

  # CUDA stuff for testing on Eagle
  if [ "${MACHINE_NAME}" == 'eagle' ]; then
    printf "\nSetting environment variables for Kokkos/CUDA...\n"
    #cmd "export OMPI_MCA_opal_cuda_support=1"
    cmd "export EXAWIND_CUDA_WRAPPER=${TRILINOS_DIR}/bin/nvcc_wrapper"
    cmd "export CUDA_LAUNCH_BLOCKING=1"
    cmd "export CUDA_MANAGED_FORCE_DEVICE_ALLOC=1"
    cmd "export KOKKOS_ARCH=SKX,Volta70"
    #cmd "export NVCC_WRAPPER_DEFAULT_COMPILER=${CXX}"
    cmd "export MPICXX_CXX=${EXAWIND_CUDA_WRAPPER}"
    cmd "export CUDACXX=$(which nvcc)"
  fi

  # Run static analysis and let ctest know we have static analysis output
  if [ "${MACHINE_NAME}" == 'rhodes' ] && [ "${COMPILER_ID}" == 'clang@10.0.0' ]; then
    printf "\nRunning cppcheck static analysis (Nalu-Wind not updated until after this step)...\n"
    cmd "rm ${LOGS_DIR}/nalu-wind-static-analysis.txt"
    cmd "cppcheck --enable=all --quiet -j 16 --output-file=${LOGS_DIR}/nalu-wind-static-analysis.txt -I ${NALU_WIND_DIR}/include ${NALU_WIND_DIR}/src"
    cmd "printf \"%s warnings\n\" \"$(wc -l < ${LOGS_DIR}/nalu-wind-static-analysis.txt | xargs echo -n)\" >> ${LOGS_DIR}/nalu-wind-static-analysis.txt"
    CTEST_ARGS="-DHAVE_STATIC_ANALYSIS_OUTPUT:BOOL=TRUE -DSTATIC_ANALYSIS_LOG=${LOGS_DIR}/nalu-wind-static-analysis.txt ${CTEST_ARGS}"
  fi

  # Unset the TMPDIR variable after building but before testing during ctest nightly script and do not overlap running tests
  if [ "${MACHINE_NAME}" == 'eagle' ]; then
    EXTRA_BUILD_NAME="-nvcc-${CUDA_VERSION}${EXTRA_BUILD_NAME}"
    CTEST_ARGS="-DUNSET_TMPDIR_VAR:BOOL=TRUE -DCTEST_DISABLE_OVERLAPPING_TESTS:BOOL=TRUE ${CTEST_ARGS}"
  fi

  # Default build type is RelWithDebInfo
  CMAKE_BUILD_TYPE=RelWithDebInfo

  # Turn on address sanitizer for clang build on rhodes
  if [ "${COMPILER_NAME}" == 'clang' ] && [ "${MACHINE_NAME}" == 'rhodes' ]; then
    printf "\nSetting up address sanitizer in Clang...\n"
    # Create blacklist for everything yaml-cpp related
    printf "\nWriting source files to blacklist file...\n"
    (set -x; printf "fun:*YAML*\n" > ${NALU_WIND_DIR}/build/asan_blacklist.txt)
    export CXXFLAGS="-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist=${NALU_WIND_DIR}/build/asan_blacklist.txt"
    printf "export CXXFLAGS=${CXXFLAGS}\n"
    # Probably should try to solve the Nalu-Wind container overflow errors sometime, but we currently ignore them
    printf "\nIgnoring container overflows...\n"
    cmd "export ASAN_OPTIONS=detect_container_overflow=0"
    # Suppress leak errors from some TPLs
    printf "\nWriting asan.supp file...\n"
    (set -x; printf "leak:libopen-pal\nleak:libmpi\nleak:libnetcdf" > ${NALU_WIND_DIR}/build/asan.supp)
    cmd "export LSAN_OPTIONS=suppressions=${NALU_WIND_DIR}/build/asan.supp"
    # Can't use optimization with the address sanitizer
    CMAKE_BUILD_TYPE=Debug
  fi

  # Explicitly set compilers to MPI compilers
  if [ "${COMPILER_NAME}" == 'gcc' ] || [ "${COMPILER_NAME}" == 'clang' ]; then
    MPI_CXX_COMPILER=mpicxx
    MPI_C_COMPILER=mpicc
    if [ "${MACHINE_NAME}" == 'eagle' ]; then
      MPI_FORTRAN_COMPILER=mpif90
    else
      MPI_FORTRAN_COMPILER=mpifort
    fi
  elif [ "${COMPILER_NAME}" == 'intel' ]; then
    MPI_CXX_COMPILER=mpiicpc
    MPI_C_COMPILER=mpiicc
    MPI_FORTRAN_COMPILER=mpiifort
  fi

  printf "\nListing cmake and compilers that will be used in ctest...\n"
  cmd "which cmake"
  cmd "which ${MPI_CXX_COMPILER}"
  cmd "which ${MPI_C_COMPILER}"
  cmd "which ${MPI_FORTRAN_COMPILER}"
  if [ "${MACHINE_NAME}" == 'eagle' ]; then
    CMAKE_CONFIGURE_ARGS="-DMPIEXEC_POSTFLAGS:STRING=--kokkos-num-devices=2 -DMPIEXEC_EXECUTABLE:STRING=mpiexec -DMPIEXEC_NUMPROC_FLAG:STRING=-np ${CMAKE_CONFIGURE_ARGS}"
  else
    cmd "which mpiexec"
    CMAKE_CONFIGURE_ARGS="-DENABLE_WIND_UTILS:BOOL=ON ${CMAKE_CONFIGURE_ARGS}"
  fi

  CMAKE_CONFIGURE_ARGS="-DENABLE_ALL_WARNINGS:BOOL=TRUE -DCMAKE_C_COMPILER:STRING=${MPI_C_COMPILER} -DCMAKE_CXX_COMPILER:STRING=${MPI_CXX_COMPILER} -DCMAKE_Fortran_COMPILER:STRING=${MPI_FORTRAN_COMPILER} -DMPI_CXX_COMPILER:STRING=${MPI_CXX_COMPILER} -DMPI_C_COMPILER:STRING=${MPI_C_COMPILER} -DMPI_Fortran_COMPILER:STRING=${MPI_FORTRAN_COMPILER} -DTrilinos_DIR:PATH=${TRILINOS_DIR} -DYAML_DIR:PATH=${YAML_DIR} -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE} ${CMAKE_CONFIGURE_ARGS}"

  # Set essential arguments for ctest
  CTEST_ARGS="-DTESTING_ROOT_DIR=${NALU_WIND_TESTING_ROOT_DIR} -DNALU_DIR=${NALU_WIND_TESTING_ROOT_DIR}/nalu-wind -DTEST_LOG=${LOGS_DIR}/nalu-wind-test-log.txt -DTEST_NORMS_FILE=${LOGS_DIR}/nalu-wind-norms.txt -DHOST_NAME=${HOST_NAME} -DEXTRA_BUILD_NAME=${EXTRA_BUILD_NAME} ${CTEST_ARGS}"

  # Set specific tolerance for GPU tests or on MacOS
  if [ "${MACHINE_NAME}" == 'eagle' ]; then
    export CXXFLAGS="-Xcudafe --diag_suppress=code_is_unreachable -Wimplicit-fallthrough=0"
    CMAKE_CONFIGURE_ARGS="-DTEST_REL_TOL=1.0e-7 -DTEST_TOLERANCE:STRING=1.0e-8 ${CMAKE_CONFIGURE_ARGS}"
  elif [ "${COMPILER_NAME}" == 'gcc' ]; then
    CMAKE_CONFIGURE_ARGS="-DTEST_REL_TOL:STRING=1.0e-13 -DTEST_TOLERANCE:STRING=1.0e-15 ${CMAKE_CONFIGURE_ARGS}"
  elif [ "${MACHINE_NAME}" == 'mac' ]; then
    CMAKE_CONFIGURE_ARGS="-DTEST_TOLERANCE:STRING=100000.0 ${CMAKE_CONFIGURE_ARGS}"
  fi

  # Allow OpenMPI to consider hardware threads as cpus and allow for oversubscription
  if [ "${COMPILER_NAME}" != 'intel' ] && [ "${MACHINE_NAME}" != 'eagle' ]; then
    CMAKE_CONFIGURE_ARGS="-DMPIEXEC_PREFLAGS:STRING=--oversubscribe ${CMAKE_CONFIGURE_ARGS}"
  fi

  printf "\nRunning CTest at $(date)...\n"
  cmd "cd ${NALU_WIND_DIR}/build"
  if [ "${MACHINE_NAME}" != 'mac' ]; then
    cmd "module list"
  fi
  cmd "ctest ${CTEST_ARGS} -DCMAKE_CONFIGURE_ARGS=\"${CMAKE_CONFIGURE_ARGS}\" -VV -S ${NALU_WIND_DIR}/reg_tests/CTestNightlyScript.cmake"
  printf "Returned from CTest at $(date)\n"

  printf "\nSaving norms...\n"
  (set -x; cd ${NALU_WIND_DIR}/build/reg_tests/test_files && find . -type f \( -name "*.norm" -o -name "*.nc" -o -name "*.dat" \) | tar -czf ${NORMS_DIR}/norms${EXTRA_BUILD_NAME}-$(date +%Y-%m-%d-%H-%M).tar.gz -T -)

  cmd "grep -E 'PASS:|FAIL:' ${NALU_WIND_DIR}/build/Testing/Temporary/LastTest_*.log* | sort -k4 -g -r > ${LOGS_DIR}/nalu-wind-norms.txt"

  printf "\n"
  printf "************************************************************\n"
  printf "Done testing Nalu-Wind with:\n"
  printf "${COMPILER_ID}\n"
  printf "trilinos@${TRILINOS_BRANCH}\n"
  printf "LIST_OF_TPLS: ${LIST_OF_TPLS}\n"
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
  #CONFIGURATION[n]='compiler_name:compiler_version:trilinos_branch:list_of_tpls'
  if [ "${MACHINE_NAME}" == 'rhodes' ]; then
    CONFIGURATIONS[0]='gcc:8.4.0:develop:fftw;tioga;hypre;openfast'
    CONFIGURATIONS[1]='gcc:8.4.0:master:fftw;tioga;hypre;openfast'
    CONFIGURATIONS[2]='intel:18.0.4:develop:fftw;tioga;hypre;openfast'
    CONFIGURATIONS[3]='clang:10.0.0:develop:fftw;tioga;hypre;openfast'
    NALU_WIND_TESTING_ROOT_DIR=/projects/ecp/exawind/nalu-wind-testing
    INTEL_COMPILER_MODULE=intel-parallel-studio/cluster.2018.4
  elif [ "${MACHINE_NAME}" == 'eagle' ]; then
    CONFIGURATIONS[0]='gcc:8.4.0:develop:cuda;tioga;hypre;openfast'
    NALU_WIND_TESTING_ROOT_DIR=/projects/hfm/exawind/nalu-wind-testing
    INTEL_COMPILER_MODULE=intel-parallel-studio/cluster.2018.4
  #elif [ "${MACHINE_NAME}" == 'mac' ]; then
  #  CONFIGURATIONS[0]='gcc:7.4.0:develop:fftw;tioga;hypre;openfast'
  #  CONFIGURATIONS[1]='clang:9.0.0-apple:develop:fftw;tioga;hypre;openfast'
  #  NALU_WIND_TESTING_ROOT_DIR=${HOME}/nalu-wind-testing
  else
    printf "\nMachine name not recognized.\n"
  fi
 
  NALU_WIND_DIR=${NALU_WIND_TESTING_ROOT_DIR}/nalu-wind
  BUILD_TEST_DIR=${NALU_WIND_TESTING_ROOT_DIR}/build-test
  SPACK_CONFIGS_DIR=${NALU_WIND_TESTING_ROOT_DIR}/spack-configs
  LOGS_DIR=${NALU_WIND_TESTING_ROOT_DIR}/logs
  NORMS_DIR=${NALU_WIND_TESTING_ROOT_DIR}/norms
  cmd "export SPACK_ROOT=${NALU_WIND_TESTING_ROOT_DIR}/spack"
 
  printf "============================================================\n"
  printf "HOST_NAME: ${HOST_NAME}\n"
  printf "NALU_WIND_TESTING_ROOT_DIR: ${NALU_WIND_TESTING_ROOT_DIR}\n"
  printf "NALU_WIND_DIR: ${NALU_WIND_DIR}\n"
  printf "BUILD_TEST_DIR: ${BUILD_TEST_DIR}\n"
  printf "LOGS_DIR: ${LOGS_DIR}\n"
  printf "NORMS_DIR: ${NORMS_DIR}\n"
  printf "SPACK_ROOT: ${SPACK_ROOT}\n"
  printf "Testing configurations:\n"
  printf " compiler_name:compiler_version:trilinos_branch:list_of_tpls\n"
  for CONFIGURATION in "${CONFIGURATIONS[@]}"; do
    printf " ${CONFIGURATION}\n"
  done
  printf "============================================================\n"
 
  if [ ! -d "${NALU_WIND_TESTING_ROOT_DIR}" ]; then
    set -e
    printf "============================================================\n"
    printf "Top level testing directory doesn't exist.\n"
    printf "Creating everything from scratch...\n"
    printf "============================================================\n"

    printf "Creating top level testing directory...\n"
    cmd "mkdir -p ${NALU_WIND_TESTING_ROOT_DIR}"
 
    printf "\nCloning Spack repo...\n"
    cmd "git clone https://github.com/spack/spack.git ${SPACK_ROOT}"
 
    printf "\nConfiguring Spack...\n"
    cmd "git clone --recursive https://github.com/exawind/build-test.git ${BUILD_TEST_DIR}"
    cmd "git clone --recursive https://github.com/jrood-nrel/spack-configs.git ${SPACK_CONFIGS_DIR}"
    cmd "cd ${SPACK_CONFIGS_DIR}/scripts && ./setup-spack.sh"
    cmd "rm ${SPACK_ROOT}/etc/spack/upstreams.yaml || true"
 
    # Checkout Nalu-Wind and meshes submodule outside of Spack so ctest can build it itself
    printf "\nCloning Nalu-Wind repo...\n"
    cmd "git clone --recursive https://github.com/exawind/nalu-wind.git ${NALU_WIND_DIR}"
    cmd "mkdir -p ${NALU_WIND_DIR}/build"
 
    printf "\nMaking job output directory...\n"
    cmd "mkdir -p ${LOGS_DIR}"

    printf "\nMaking norm archive directory...\n"
    cmd "mkdir -p ${NORMS_DIR}"
 
    printf "============================================================\n"
    printf "Done setting up testing directory\n"
    printf "============================================================\n"
    set +e
  fi
 
  printf "\nLoading Spack...\n"
  cmd "source ${SPACK_ROOT}/share/spack/setup-env.sh"

  printf "\n"
  printf "============================================================\n"
  printf "Starting testing loops...\n"
  printf "============================================================\n"
 
  # Test Nalu-Wind for the list of configurations
  for CONFIGURATION in "${CONFIGURATIONS[@]}"; do
    CONFIG=(${CONFIGURATION//:/ })
    COMPILER_NAME=${CONFIG[0]}
    COMPILER_VERSION=${CONFIG[1]}
    TRILINOS_BRANCH=${CONFIG[2]}
    LIST_OF_TPLS=${CONFIG[3]}
 
    printf "\nRemoving previous test log for uploading to CDash...\n"
    cmd "rm ${LOGS_DIR}/nalu-wind-test-log.txt ${LOGS_DIR}/nalu-wind-norms.txt"
    (test_configuration) 2>&1 | tee -i ${LOGS_DIR}/nalu-wind-test-log.txt
  done

  printf "============================================================\n"
  printf "Done with testing loops\n"
  printf "============================================================\n"
  printf "============================================================\n"
  printf "Final steps\n"
  printf "============================================================\n"
 
  if [ "${MACHINE_NAME}" == 'eagle' ] || [ "${MACHINE_NAME}" == 'rhodes' ]; then
    printf "\nSetting permissions...\n"
    cmd "chmod -R a+rX,go-w ${NALU_WIND_TESTING_ROOT_DIR}"
  fi

  if [ "${MACHINE_NAME}" == 'rhodes' ]; then
    printf "\nSetting group...\n"
    cmd "chgrp -R windsim ${NALU_WIND_TESTING_ROOT_DIR}"
  fi

  printf "============================================================\n"
  printf "Done!\n"
  printf "$(date)\n"
  printf "============================================================\n"
}

main "$@"
