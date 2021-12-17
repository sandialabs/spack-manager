#!/bin/bash -l

source /nopt/nrel/ecom/hpacf/env.sh
module load gcc
module load binutils
module load git
module load python

mkdir -p /scratch/${USER}/.tmp
export TMPDIR=/scratch/${USER}/.tmp
