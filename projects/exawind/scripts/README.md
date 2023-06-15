# Spack scripts

This section is not very mature.  Eventually I'd like to have these be a bunch of scripts that users and devs can use so they don't have to call spack commands directly at all.
RIght now the main scripts are the `environment_update.py` and the `create_default_environment.py`. 

`environment_updater.py` will update a single environment or a list of environments and can be run with `sbatch` to maximize parallelism of the build process.
There is still more that can be done on the latter point.

`create_default_environment.py` will copy the config files to setup a base environment that should then be customized as needed.

