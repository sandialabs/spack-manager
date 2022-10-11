#! /bin/bash

export SPACK_MANAGER=/projects/wind/wind-testing-gpu
export SPACK_MANAGER_GOLDS_DIR=/projects/wind/golds-gpu

source $SPACK_MANAGER/scripts/snl_nightly_test.sh
run_snl_nightlies
