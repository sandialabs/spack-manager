#! /bin/bash

export SPACK_MANAGER=/projects/wind/wind-testing-cpu
export SPACK_MANAGER_GOLDS_DIR=/projects/wind/golds-cpu

source $SPACK_MANAGER/scripts/snl_nightly_test.sh
run_snl_nightlies
