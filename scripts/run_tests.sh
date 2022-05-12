#!/bin/bash

# Expected to be run at top level spack-manager directory
export SPACK_MANAGER=$(pwd)
source ${SPACK_MANAGER}/start.sh
spack-start
spack -C ${SPACK_MANAGER}/configs/base unit-test --extension scripting
