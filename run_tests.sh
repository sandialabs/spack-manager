#! /bin/bash
SPACK_MANAGER=$(pwd)
export PYTHONPATH=${SPACK_MANAGER}/scripts

pytest --ignore spack
