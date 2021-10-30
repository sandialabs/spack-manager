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
export PYTHONPATH=${PYTHONPATH}:${SPACK_MANAGER}/scripts:${SPACK_MANAGER}/spack-scripting/scripting/cmd
source ${SPACK_ROOT}/share/spack/setup-env.sh

if [[ -z $(spack config --scope site blame config | grep spack-scripting) ]]; then
    spack config --scope site add config:extensions:['$spack/../spack-scripting']
fi

export SPACK_MANAGER_MACHINE=$(${SPACK_MANAGER}/scripts/find_machine.py)
if [[ "${SPACK_MANAGER_MACHINE}" == "NOT-FOUND" ]]; then
    echo "Machine not found."
fi
export PATH=${PATH}:${SPACK_MANAGER}/scripts
