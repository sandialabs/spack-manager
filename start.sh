#!/bin/bash

cmd() {
  echo "+ $@"
  eval "$@"
}

########################################################
# Tests
########################################################
if [[ -z ${SPACK_MANAGER} ]]; then
    echo "Env variable SPACK_MANAGER not set. You must set this variable."
    exit 125
fi

if [[ ! -x $(which python3) ]]; then
    echo "Warning: spack-manager is only designed to work with python 3."
    echo "You may use spack, but spack-manager specific commands will fail."
fi
 
# function to initialize spack-manager's spack instance
function spack-start() {
  if [[ -z ${SPACK_MANAGER_MACHINE} ]]; then
    export SPACK_ROOT=${SPACK_MANAGER}/spack
    export SPACK_DISABLE_LOCAL_CONFIG=true
    export SPACK_USER_CACHE_PATH=${SPACK_MANAGER}/.cache
    export PYTHONPATH=${PYTHONPATH}:${SPACK_MANAGER}/scripts:${SPACK_MANAGER}/spack-scripting/scripting/cmd:${SPACK_MANAGER}/spack-scripting/scripting
    source ${SPACK_ROOT}/share/spack/setup-env.sh
  
    # Clean Spack misc caches
    # Put this back in if outdated caches directory still causes problems when updating Spack submodule
    #spack clean -m
    
    if [[ -z $(spack config --scope site blame config | grep spack-scripting) ]]; then
        spack config --scope site add "config:extensions:[${SPACK_MANAGER}/spack-scripting]"
    fi
    
    export SPACK_MANAGER_MACHINE=$(spack manager find-machine)
    if [[ "${SPACK_MANAGER_MACHINE}" == "NOT-FOUND" ]]; then
        echo "Machine not found."
    fi
    if [[ -n "$(${SPACK_MANAGER}/scripts/supported_external_paths.py)" ]]; then
        export SPACK_MANAGER_EXTERNAL=$(${SPACK_MANAGER}/scripts/supported_external_paths.py)
    fi
    export PATH=${PATH}:${SPACK_MANAGER}/scripts
  fi
}

# function to quickly activate an environment
function quick-activate() {
  cmd "spack-start"
  cmd "spack env activate -p -d $1"
}

# convenience function for quickly creating an environment
# and activating it in the current shell
function quick-create() {
  cmd "spack-start"
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "*************************************************************
HELP MESSAGE:
quick-create sets up a basic spack environment
    
The next typical steps after running this command are to add specs
and calling spack manager develop to clone dev specs, adding externals
etc.

Please note that if you wish to specify multiple specs with spaces 
as an input to this command you need to wrap them in quotes as follows:

\"'amr-wind@main build_type=Debug' nalu-wind@master 'exawind@master build_type=Debug'\"
    
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
  EPATH=$(cat $SPACK_MANAGER/.tmp/created_env_path.txt)
  cmd "spack env activate --dir ${EPATH} --prompt"
}

# same as quick-create but calls create-env-dev instead
# can be used to add externals
function quick-create-dev() {
  cmd "spack-start"
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "*************************************************************
HELP MESSAGE:
quick-create-dev sets up a developer environment
where all specs are develop specs that will be automatically cloned
from the default repos

Please note that for specifying multiple specs with spaces you need to 
wrap them in quotes as follows:

\"'amr-wind@main build_type=Debug' nalu-wind@master 'exawind@master build_type=Debug'\"
    
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
  EPATH=$(cat $SPACK_MANAGER/.tmp/created_env_path.txt)
  cmd "spack env activate --dir ${EPATH} --prompt"
}

# function to create, activate, concretize and attempt to install a develop environment all in one step
function quick-develop() {
  cmd "spack-start"
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

Please note that for specifying multiple specs with spaces you need to 
wrap them in quotes as follows:

\"'amr-wind@main build_type=Debug' nalu-wind@master 'exawind@master build_type=Debug'\"
    
The base command and it's help are echoed below:
    
"
    cmd "spack manager create-dev-env $@"
    echo "*************************************************************"
    return
  fi
  cmd "spack manager create-dev-env $*"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-develop prematurely\n"
    return 1
  fi
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    return
  fi
  EPATH=$(cat $SPACK_MANAGER/.tmp/created_env_path.txt)
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
  cmd "spack install"
}

# function to remove spack prompt from the shell
function remove-spack-prompt() {
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "This command removes a spack added shell prompt (if it exists) that signifies the current environment name."
  fi
  if [[ -n "${SPACK_OLD_PS1}" ]]; then
    PS1=${SPACK_OLD_PS1}
    unset SPACK_OLD_PS1
  fi
}
