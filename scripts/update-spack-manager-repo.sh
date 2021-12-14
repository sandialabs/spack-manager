#!/bin/bash -l

# Script for updating the spack-manager repo before it's used in running the tests.

printf "\n$(date)\n"
printf "\nJob is running on ${HOSTNAME}\n"
printf "\nUpdating spack-manager repo...\n"
(set -x; pwd && git fetch --all && git reset --hard origin/main && git clean -df && git submodule update && git status -uno) 2>&1
