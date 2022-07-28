#!/bin/bash
#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#

cmd() {
  echo "+ $@"
  eval "$@"
}

########################################################
# Tests
########################################################
if [[ -z ${SPACK_MANAGER} ]]; then
  echo "Env variable SPACK_MANAGER not set. You must set this variable."
  return 125
fi

if [[ ! -x $(which python3) ]]; then
  echo "Warning: spack-manager is only designed to work with python 3."
  echo "You may use spack, but spack-manager specific commands will fail."
fi

# convenience function for getting to the spack-manager directory
function _cd_sm() {
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Convenience function for navigating to the spack-manager directory"
    return
  fi
  cd ${SPACK_MANAGER}
}

# function to initialize spack-manager's spack instance
function _spack_start() {
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "This function loads spack into your active shell"
    return
  fi
  source ${SPACK_MANAGER}/scripts/spack_start.sh
}

# function to quickly activate an environment
function _quick_activate() {
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "This function loads spack and activates the spack environment whose directory you provide as an argument"
    return
  fi
  cmd "_spack_start"
  cmd "spack env activate -p -d $1"
}

# convenience function for quickly creating an environment
# and activating it in the current shell
function _quick_create() {
  cmd "_spack_start"
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "*************************************************************
HELP MESSAGE:
quick-create sets up a basic spack environment

The next typical steps after running this command are to add specs
and calling spack manager develop to clone dev specs, adding externals
etc.

The base command and it's help are echoed below:

"
    cmd "spack manager create-env $@"
    echo "*************************************************************"
    return
  fi
  cmd "spack manager create-env $@"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-create prematurely\n"
    return 1
  fi
  EPATH=$(cat ${SPACK_MANAGER}/.tmp/created_env_path.txt)
  cmd "spack env activate --dir ${EPATH} --prompt"
}

# same as quick-create but calls create-env-dev instead
# can be used to add externals
function _quick_create_dev() {
  cmd "_spack_start"
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "*************************************************************
HELP MESSAGE:
quick-create-dev sets up a developer environment
where all specs are develop specs that will be automatically cloned
from the default repos

The next typical steps after running this command are to add externals if
you want them, or run spack install.

The base command and it's help are echoed below:

"
    cmd "spack manager create-dev-env $@"
    echo "*************************************************************"
    return
  fi
  cmd "spack manager create-dev-env $@"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-create prematurely\n"
    return 1
  fi
  EPATH=$(cat ${SPACK_MANAGER}/.tmp/created_env_path.txt)
  cmd "spack env activate --dir ${EPATH} --prompt"
}

# function to create, activate, concretize and attempt to install a develop environment all in one step
function _quick_develop() {
  cmd "_spack_start"
  # since we want this to run in the active shell
  # we mush manually return instead of exiting with set -e
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-develop prematurely\n"
    return 1
  fi
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "*************************************************************
HELP MESSAGE:
quick-develop sets up a developer environment and installs it

This command is designed to require minimal arguments and simple setup
with the caveat of accepting all the defaults for:

- repo and branch cloned for your packages
- latest external snapshot with the default compilers/configurations

The base command and it's help are echoed below:

"
    cmd "spack manager create-dev-env $@"
    echo "*************************************************************"
    return
  fi
  cmd "spack manager create-dev-env $*"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick_develop prematurely\n"
    return 1
  fi
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    return
  fi
  EPATH=$(cat ${SPACK_MANAGER}/.tmp/created_env_path.txt)
  cmd "spack env activate --dir ${EPATH} --prompt"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-develop prematurely\n"
    return 1
  fi
  cmd "spack manager external --latest"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-develop prematurely\n"
    return 1
  fi
}

# function to remove spack prompt from the shell
function _remove_spack_prompt() {
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "This command removes a spack added shell prompt (if it exists) that signifies the current environment name."
    return
  fi
  if [[ -n "${SPACK_OLD_PS1}" ]]; then
    PS1=${SPACK_OLD_PS1}
    unset SPACK_OLD_PS1
  fi
}

# function for diving into the build environment from a spack build
function _build_env_dive() {
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "This command will setup and dive into the build environment of the spec provided in a new subshell, and then move into the build directory."
    return
  fi
  if [[ -z ${SPACK_ENV} ]]; then
    echo "You must have an active environment to use build_env_dive."
    return 1
  fi
  cmd "spack build-env --dump ${SPACK_MANAGER}/.tmp/spack-build-env.txt $*"
  cmd "bash --rcfile <(echo '. ${SPACK_MANAGER}/.tmp/spack-build-env.txt; spack cd -b $*')"
}

# function for cleaning spack-manager and spack directories
function _sm_clean(){
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "This command will clean out spack and spack-manager caches and other problematic directories"
    return
  fi
  echo "Remove user cache of configs:"
  cmd "rm -rf ~/.spack"
  echo "Use the native Spack clean system":
  cmd "spack clean --all"
  echo "Cleaning out pycache from spack-manager repos:"
  cmd "find ${SPACK_MANAGER}/repos -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete"
}

alias cd-sm='_cd_sm'
alias spack-start='_spack-start'
alias quick-activate='_quick_activate'
alias quick-create='_quick_create'
alias quick-create-dev='_quick_create_dev'
alias quick-develop='_quick_develop'
alias remove-spack-prompt='_remove_spack_prompt'
alias build-env-dive='_build_env_dive'
alias sm-clean='_sm_clean'
