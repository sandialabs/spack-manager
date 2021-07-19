#! /bin/bash

########################################################
# Tests
########################################################
if [[ -z ${SPACK_MANAGER} ]]; then
    echo "Env variable SPACK_MANAGER not set. You must set this variable."
    exit 125
fi

########################################################
# Environment stuff
########################################################
export SPACK_ROOT=${SPACK_MANAGER}/spack
export SPACK_MANAGER_MACHINE=$(${SPACK_MANAGER}/scripts/find_machine.py)
if [[ "${SPACK_MANAGER_MACHINE}" == "NOT-FOUND" ]]; then
    echo "Machine not found."
    exit 125
fi
export SPACK_CONFIG_BASE=${SPACK_MANAGER}/configs/base
export SPACK_CONFIG_MACHINE=${SPACK_MANAGER}/configs/${SPACK_MANAGER_MACHINE}
source ${SPACK_ROOT}/share/spack/setup-env.sh
#export PATH=${PATH}:${SPACK_MANAGER}/scripts

########################################################
# Simple functions for making config scoping easier to use
########################################################
function sspack()
{
  spack -C ${SPACK_CONFIG_BASE} -C ${SPACK_CONFIG_MACHINE} "$@"
}
function spack-switch-config()
{
  export SPACK_CONFIG=$1
}
