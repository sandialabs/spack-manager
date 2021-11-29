# function to initialize spack-manager's spack instance
function spack-start(){
  source ${SPACK_MANAGER}/start.sh
}
# function to quickly activate an environment
function quick-activate(){
  spack-start
  spack env activate -d $1
}
# function to wrap spack manager calls for shell modification
# i.e. shell-wrapped-spack
function swspack(){
  spack_command="spack $@"
  if [[ "$*" == *create-env* && "$*" == *-a* ]]; then
    eval $( ${spack_command} )
  else
    eval ${spack_command}
  fi
}
