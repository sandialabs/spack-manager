#!/bin/bash -l

#SBATCH -J build-exawind-azure
#SBATCH -o %x.o%j
#SBATCH -t 24:00:00
#SBATCH -N 1

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

LOCALSSD=/mnt/resource
EXAWINDDIR=${LOCALSSD}/exawind

export TMPDIR=${LOCALSSD}/.tmp
export INSTALLDIR=/lustre/${USER}/exawind/software/opt
export MODULEDIR=/lustre/${USER}/exawind/software/modules
export SPACK_MANAGER=${EXAWINDDIR}/spack-manager

cmd "sudo yum install -y python3"
cmd "sudo chmod -R a+rwX ${LOCALSSD}"

cmd "bash -l"
if [ ! -z "${TMPDIR}" ]; then
  cmd "rm -rf ${TMPDIR}"
fi
if [ ! -z "${EXAWINDDIR}" ]; then
  cmd "rm -rf ${EXAWINDDIR}"
fi
if [ ! -z "${INSTALLDIR}" ]; then
  cmd "rm -rf ${INSTALLDIR}"
fi
cmd "mkdir -p ${TMPDIR}"
cmd "mkdir -p ${EXAWINDDIR}"
cmd "mkdir -p ${INSTALLDIR}"
cmd "mkdir -p ${MODULEDIR}"
cmd "cd ${EXAWINDDIR}"
cmd "git clone --recursive https://github.com/sandialabs/spack-manager.git"
cmd "cd spack-manager && ./scripts/install-exawind.sh"
