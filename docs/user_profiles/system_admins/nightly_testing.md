# Nightly Testing with Spack-Manager

Spack-manager has all the necessary components implemented to test and report results for a project to CDash each night. In the following section we will be using the Exawind project as an example to explain the testing process.

## Cron Job

Starting from the nightly cronjob, the Exawind testing job is invoked as such:
```
#Exawind tests
0 0 * * * /bin/bash -c "export SPACK_MANAGER=/projects/ecp/exawind/exawind-testing/spack-manager && cd \${SPACK_MANAGER} && \${SPACK_MANAGER}/scripts/update-spack-manager-repo.sh &> \${SPACK_MANAGER}/logs/last-spack-manager-repo-update.txt && \${SPACK_MANAGER}/scripts/run-exawind-nightly-tests.sh &> \${SPACK_MANAGER}/logs/last-exawind-test-script-invocation.txt"
```

In the cron job specification, `SPACK_MANAGER` is set. Then the spack-manager repo used for the testing is updated each night with the changes to spack-manager so it's always up-to-date. Next the `run-exawind-nightly-tests.sh` script is run.

## Test Invocation

The `run-exawind-nightly-tests.sh` script generates another script on the fly. This is done because depending on what machine it is on, it may need to submit a job to run the tests, which requires a script to be submitted. Spack-manager finds the machine it is running on and runs the generated test script using different methods for different machines.

For Exawind, the test script manages much of the archiving of gold files for each particular application in the `golds` directory of spack-manager. It then finds the set of tests that machine is intended to run which are listed in a file in the `env-templates` directory. These yaml files are lists of specs to be installed and tested. Spack-manager uses python class inheritance to add special testing packages with `*-nightly` suffixes onto preexisting packages within Spack or the custom spack-manager package repos in the `repos` directory. These nightly packages manage the CMake configured options that get passed to the CTest nightly scripts with the repos for each tested package. Spack-manager then sets up a Spack environment with the testing yaml file, activates the environment, uninstalls all the nightly test packages installed from the previous test runs and then concretizes and installs the latest git repos of the packages. By doing multiple `spack install` processes at the same time, Spack is able to parallelize the disjoint packages that have no dependencies on one another and test multiple packages on a system at once in a very organized and separate fashion. Once the tests complete, each package reports their own results to CDash and the test script then archives the generated gold files.
