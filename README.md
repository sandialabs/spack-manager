# Spack Manager

This is a simple collection of scripts to unify spack usage across multiple machines and to allow control over packages across different architectures that may be shared on the same file system (and spack instance). Right now this system is focused on serving the needs of the [ExaWind project](https://github.com/ExaWind), but the hope is it can be scaled to serve multiple projects simultaneously in the future.

Spack is included as a submodule for now to ensure that all the systems are running the same (or close to the same) spack version.

Most of the functionality relies on defining the `SPACK_MANAGER` environment variable in your environment prior to running these i.e. `.bashrc` or `.bash_profile`.  This mainly serves as an absolute reference and could be replaced with local references in the future.

The main goals of `spack-manager` are to:

1) Provide a sycronized [spack](https://github.com/spack/spack) version across multiple machines and platforms
2) Organize package extensions and tools for features that we a) don't want in the main spack repo or b) need quick fixes that should then be merged into spack

There are a collection of scripts that will help with:
a) [setting up developer workflows](docs/developer_tutorial.md)
b) creating deployable modules for HPC environments
c) running nightly tests

In all of these objectives the scripts are just simple wrappers around [spack](https://github.com/spack/spack).
All of these features can be deployed manually through spack commands and carefully constructed spack environments.
As such, it is recommended that those utilizing this tool also become familiar with the features of
spack and consult [spack's documentation](https://spack.readthedocs.io/en/latest/)
