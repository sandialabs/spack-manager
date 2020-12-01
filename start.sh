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
export SPACK_CONFIG=${SPACK_MANAGER}/configs/snl-ews
source ${SPACK_ROOT}/share/spack/setup-env.sh

########################################################
# Simple scripts for making it easier to use
########################################################
function sspack()
{
  spack -C ${SPACK_CONFIG} "$@"
}
function spack-switch-config()
{
  export SPACK_CONFIG=$1
}
