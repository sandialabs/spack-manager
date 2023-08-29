#!/bin/bash

# Need > python-3.7; do not use Anaconda

echo -e "Creating container on:  ${NERSC_HOST} ..."

source $SPACK_MANAGER/start.sh 
spack-start
export SPACK_MANAGER_MACHINE=perlmutter
create-exawind-snapshot.sh
spack install
spack clean -a
rm -rf /tmp/root
