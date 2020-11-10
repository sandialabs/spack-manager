#! /bin/bash

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