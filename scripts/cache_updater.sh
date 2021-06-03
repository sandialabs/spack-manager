for ii in $(spack find --format "yyy {version} /{hash}" |
    grep -v -E "^(develop^master)" |
    grep "yyy" |
    cut -f3 -d" ")
do
  spack buildcache create -af -d ${SPACK_MANAGER}/cache --only=package $ii
done
