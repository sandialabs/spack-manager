#!/bin/bash -l

# Script for updating the spack-manager repo before it's used in running the tests.

printf "$(date)\n"
printf "Job is running on ${HOSTNAME}\n"
printf "\n\nUpdating build-test repo...\n\n"
(set -x; pwd && git fetch --all && git reset --hard origin/main && git clean -df && git status -uno) 2>&1
