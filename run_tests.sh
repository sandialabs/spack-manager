#! /bin/bash
export SPACK_MANAGER=$(pwd)
source start.sh

spack unit-test --extension scripting
