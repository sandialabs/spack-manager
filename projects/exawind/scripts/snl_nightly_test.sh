#! /bin/bash

function set_gold_perms() {
  chgrp -R wg-sierra-users $1
  chmod -R o-rwx $1
  chmod -R g+rwX $1
  find $1 -type d | xargs chmod g+s
}

function set_log_perms() {
  chgrp wg-sierra-users $1
  chmod g+rx $1
  chgrp -R wg-sierra-users $1/logs
  chmod -R g+rX $1/logs
}

function run_snl_nightlies() {
  cd $SPACK_MANAGER

  $SPACK_MANAGER/scripts/update-spack-manager-repo.sh &> $SPACK_MANAGER/logs/last-spack-manager-repo-update.txt
  $SPACK_MANAGER/scripts/run-exawind-nightly-tests.sh &> $SPACK_MANAGER/logs/last-exawind-test-script-invocation.txt

  set_log_perms $SPACK_MANAGER
  set_gold_perms ${SPACK_MANAGER_GOLDS_DIR}-stable
  set_gold_perms ${SPACK_MANAGER_GOLDS_DIR}-develop
}
