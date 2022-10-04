#! /bin/bash

function set_gold_perms() {
  chgrp -R wg-sierra-users $1
  chmod -R o-rwx $1
  chmod -R g+rwX $1
  find $1 -type d | xargs chmod g+s
}

export SPACK_MANAGER=/projects/wind/wind-testing-cpu
export SPACK_MANAGER_GOLDS_DIR=/projects/wind/golds-cpu
cd $SPACK_MANAGER

$SPACK_MANAGER/scripts/update-spack-manager-repo.sh &> $SPACK_MANAGER/logs/last-spack-manager-repo-update.txt
$SPACK_MANAGER/scripts/run-exawind-nightly-tests.sh &> $SPACK_MANAGER/logs/last-exawind-test-script-invocation.txt

set_gold_perms ${SPACK_MANAGER_GOLDS_DIR}-stable
set_gold_perms ${SPACK_MANAGER_GOLDS_DIR}-develop

chgrp wg-sierra-users $SPACK_MANAGER
chgrp -R wg-sierra-users $SPACK_MANAGER/logs
chmod -R g+rx $SPACK_MANAGER/logs
