#
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
#
for ii in $(spack find --format "yyy {version} /{hash}" |
    grep -v -E "^(develop^master)" |
    grep "yyy" |
    cut -f3 -d" ")
do
  spack buildcache create -af -d ${SPACK_MANAGER}/cache --only=package $ii
done
