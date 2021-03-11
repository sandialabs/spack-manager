# Spack Manager

This is a simple collection of scripts to unify spack usage across multiple machines and to allow control over packages across different architectures that may be shared on the same file system (and spack instance). Right now this system is focused on serving the needs of the [ExaWind project](https://github.com/ExaWind), but the hope is it can be scaled to serve multiple projects simultaneously in the future.

Spack is included as a submodule for now to ensure that all the systems are running the same (or close to the same) spack version.

Most of the functionality relies on defining the `SPACK_MANAGER` environment variable in your environment prior to running these i.e. `.bashrc` or `.bash_profile`.  This mainly serves as an absolute reference and could be replaced with local references in the future.

