# Spack Manager

This is a simple collection of scripts to unify spack usage across multiple machines and to allow control over packages across different architectures that may be shared on the same file system (and spack instance). Right now this system is focused on serving the needs of the [ExaWind project](https://github.com/ExaWind), but the hope is it can be scaled to server multiple projects simultaneously in the future.

Spack is included as a submodule for now to ensure that all the systems are running the same (or close to the same) spack version.

Most of the functionality relies on defining the `SPACK_MANAGER` environment variable in your environment prior to running these i.e. `.bashrc` or `.bash_profile`.  This mainly serves as an absolute reference and could be replaced with local references in the future.

## Setting up a machine
Beyond the usual `git clone` `git submodule init` and `git submodule update` for this repository one should do the following.

1) If there is no exisiting environment in the [environments](https://github.com/psakievich/spack-manager/environments) folder create one.
Additional configurations should be added to the [configs](https://github.com/psakievich/spack-manager/configs) directory that can be included in the environment.
2) Navigate inside this directory and create the environment `spack env create -d .`
3) Activate the enivronment `spack env activate -d .`
4) Concretize `spack concretize` and build the packages `spack install`

The to distribute this environment to others who can use the packages for TPL caching for their own developmen process or for use with `spack dev-build`s:

5) Create a loading script `spack env loads -r`

This loading script can be renamed and stored in a common directory, or shared in whatever manner you choose.  My current plan is to do something like this:
`cp loads $SPACK_MANAGER/LoadingDock/$(spack arch)` 

This is so users can load environments specific for the architecture they are on.  

