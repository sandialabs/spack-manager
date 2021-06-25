#!/bin/bash

#Script for deducing machine name within list of known machines

OS=$(uname -s)

if [[ "${OS}" == "Darwin" ]]; then
  OSX=$(sw_vers -productVersion)
  case "${OSX}" in
    10.1*)
      SPACK_MANAGER_MACHINE=mac
    ;;
    11.*)
      SPACK_MANAGER_MACHINE=mac
    ;;
  esac
elif [[ "${OS}" == "Linux" ]]; then
  case "${NREL_CLUSTER}" in
    eagle)
      SPACK_MANAGER_MACHINE=eagle
    ;;
  esac
  MYHOSTNAME=$(hostname -s)
  case "${MYHOSTNAME}" in
    rhodes)
      SPACK_MANAGER_MACHINE=rhodes
    ;;
  esac
fi

if [[ "${SPACK_MANAGER_MACHINE}" == "eagle" ]] || \
   [[ "${SPACK_MANAGER_MACHINE}" == "rhodes" ]] || \
   [[ "${SPACK_MANAGER_MACHINE}" == "mac" ]]; then
  printf "Machine is detected as ${SPACK_MANAGER_MACHINE}.\n"
  export SPACK_MANAGER_MACHINE=${SPACK_MANAGER_MACHINE}
else
  printf "\nMachine name not found.\n"
  export SPACK_MANAGER_MACHINE="NOT-FOUND"
fi

