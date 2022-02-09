#!/bin/bash

# Expected to be run at top level spack-manager directory
export SPACK_MANAGER=$(pwd)
source ${SPACK_MANAGER}/start.sh

spack unit-test --extension scripting
