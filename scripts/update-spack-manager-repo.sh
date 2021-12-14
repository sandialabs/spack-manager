#!/bin/bash -l

# Script for updating the spack-manager repo before it's used in running the tests.

printf "Job is running on ${HOSTNAME}\n"
printf "\nRun at $(date)\n"
printf "\nUpdating spack-manager repo...\n"
(set -x; pwd && git fetch --all && git reset --hard origin/jrood/develop_specs && git clean -df && git submodule update && git status -uno) 2>&1
