cmd() {
  echo "+ $@"
  eval "$@"
}
# function to initialize spack-manager's spack instance
function spack-start() {
  source ${SPACK_MANAGER}/start.sh
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
  cmd "spack manager create-env $@"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-create prematurely\n"
    return 1
  fi
  EPATH=$(cat $SPACK_MANAGER/.tmp/created_env_path.txt)
  cmd "spack env activate --dir ${EPATH} --prompt"
}
# function to create, activate, concretize and attempt to install a develop environment all in one step
function quick-develop() {
  # Trap and kill background processes
  trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

  # since we want this to run in the active shell
  # we mush manually return instead of exiting with set -e

  cmd "spack-start"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-develop prematurely\n"
    return 1
  fi
  cmd "spack manager create-dev-env $*"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-develop prematurely\n"
    return 1
  fi
  EPATH=$(cat $SPACK_MANAGER/.tmp/created_env_path.txt)
  cmd "spack env activate --dir ${EPATH} --prompt"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-develop prematurely\n"
    return 1
  fi
  cmd "spack concretize -f"
  if [[ $? != 0 ]]; then
    printf "\nERROR: Exiting quick-develop prematurely\n"
    return 1
  fi
  cmd "spack install"
}
