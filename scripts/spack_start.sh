#!/bin/bash

if [[ -z ${SPACK_MANAGER_MACHINE} ]]; then
  export SPACK_ROOT=${SPACK_MANAGER}/spack
  export SPACK_DISABLE_LOCAL_CONFIG=true
  export SPACK_USER_CACHE_PATH=${SPACK_MANAGER}/.cache
  export PYTHONPATH=${PYTHONPATH}:${SPACK_MANAGER}/scripts:${SPACK_MANAGER}/spack-scripting/scripting/cmd:${SPACK_MANAGER}/spack-scripting/scripting
  source ${SPACK_ROOT}/share/spack/setup-env.sh

  # Clean Spack misc caches
  # Put this back in if outdated caches directory still causes problems when updating Spack submodule
  #spack clean -m

  if [[ -z $(spack config --scope site blame config | grep spack-scripting) ]]; then
    spack config --scope site add "config:extensions:[${SPACK_MANAGER}/spack-scripting]"
  fi

  export SPACK_MANAGER_MACHINE=$(spack manager find-machine)
  if [[ "${SPACK_MANAGER_MACHINE}" == "NOT-FOUND" ]]; then
    echo "Machine not found."
  fi
  if [[ -n "$(${SPACK_MANAGER}/scripts/supported_external_paths.py)" ]]; then
    export SPACK_MANAGER_EXTERNAL=$(${SPACK_MANAGER}/scripts/supported_external_paths.py)
  fi
  export PATH=${PATH}:${SPACK_MANAGER}/scripts
fi
