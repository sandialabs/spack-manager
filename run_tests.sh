#! /bin/bash
SPACK_MANAGER=$(pwd)
source start.sh

spack unit-test --extension scripting
