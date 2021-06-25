#!/bin/bash

#Script for deducing machine name within list of known machines

OS=$(uname -s)

if [ ${OS} == 'Darwin' ]; then
  OSX=$(sw_vers -productVersion)
  case "${OSX}" in
    10.12*)
      MACHINE=mac
    ;;
    10.13*)
      MACHINE=mac
    ;;
    10.14*)
      MACHINE=mac
    ;;
    10.15*)
      MACHINE=mac
    ;;
    11.*)
      MACHINE=mac
    ;;
  esac
elif [ ${OS} == 'Linux' ]; then
  case "${NREL_CLUSTER}" in
    eagle)
      MACHINE=eagle
    ;;
  esac
  MYHOSTNAME=$(hostname -s)
  case "${MYHOSTNAME}" in
    rhodes)
      MACHINE=rhodes
    ;;
  esac
fi

# Impose machine-specific configurations for Spack
if [ "${MACHINE}" == 'eagle' ] || \
   [ "${MACHINE}" == 'rhodes' ] || \
   [ "${MACHINE}" == 'mac' ]; then

  printf "Machine is detected as ${MACHINE}.\n"

  #if [ ${MACHINE} == 'eagle' ] || [ ${MACHINE} == 'rhodes' ]; then
  #  OS=linux
  #elif [ "${MACHINE}" == 'mac' ]; then
  #  OS=darwin
  #fi

  #THIS_REPO_DIR=..

  #All machines do this
  #(set -x; mkdir -p ${SPACK_ROOT}/etc/spack/${OS})
  #(set -x; cp ${THIS_REPO_DIR}/configs/base/*.yaml ${SPACK_ROOT}/etc/spack/)
  #(set -x; cp ${THIS_REPO_DIR}/configs/${MACHINE}/packages.yaml ${SPACK_ROOT}/etc/spack/${OS}/)
  #(set -x; cp ${THIS_REPO_DIR}/configs/${MACHINE}/config.yaml ${SPACK_ROOT}/etc/spack/${OS}/)
  #(set -x; cp -R ${THIS_REPO_DIR}/custom ${SPACK_ROOT}/var/spack/repos/)

else
  printf "\nMachine name not found.\n"
fi

