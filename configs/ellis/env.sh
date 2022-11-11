#!/bin/bash -l

umask u=rwx,go=rx,o=rx

# HPACF Environment
source /projects/hpacf/apps/env.sh
module load gcc
module load binutils
module load git
module load python
