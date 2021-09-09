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
export PYTHONPATH=${PYTHONPATH}:${SPACK_MANAGER}/scripts
source ${SPACK_ROOT}/share/spack/setup-env.sh
export SPACK_MANAGER_MACHINE=$(${SPACK_MANAGER}/scripts/find_machine.py)
if [[ "${SPACK_MANAGER_MACHINE}" == "NOT-FOUND" ]]; then
    echo "Machine not found."
fi
export PATH=${PATH}:${SPACK_MANAGER}/scripts
