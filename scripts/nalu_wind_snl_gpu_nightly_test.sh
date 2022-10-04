#! /bin/bash

export SPACK_MANAGER=/projects/wind/wind-testing-gpu
export SPACK_MANAGER_GOLDS_DIR=/projects/wind/golds-gpu
cd $SPACK_MANAGER

$SPACK_MANAGER/scripts/update-spack-manager-repo.sh &> $SPACK_MANAGER/logs/last-spack-manager-repo-update.txt
$SPACK_MANAGER/scripts/run-exawind-nightly-tests.sh &> $SPACK_MANAGER/logs/last-exawind-test-script-invocation.txt

chgrp -R wg-sierra-users $SPACK_MANAGER_GOLDS_DIR
chmod -R o-rwx $SPACK_MANAGER_GOLDS_DIR
chmod -R g+rwX $SPACK_MANAGER_GOLDS_DIR
find $SPACK_MANAGER_GOLDS_DIR -type d | xargs chmod g+s
