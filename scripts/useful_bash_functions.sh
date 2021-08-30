# function to initialize spack-manager's spack instance
function spack-start(){
  source ${SPACK_MANAGER}/start.sh
}
# function to quickly activate an environment
function quick-activate(){
  spack-start
  spack env activate -d $1
}
