# Spack Manager

This is a simple collection of scripts to unify the spack usage.
Spack is included as a submodule for now to ensure that all the systems are running
the same (or close to the same) spack version.

The goal of this manager is to allow building and caching of TPL's and provide a consistent environment for deploying executables across multiple machines and architectures via 1 spack instance.
It will hopefully also manage nightly testing scripts.

TODO
- [] Correct config files for the machines
- [] Generate build environments for 
  - [] darwin
  - [] general cee x86-64
  - [] ascicgpu cuda builds
  - [] skybridge
  - [] ghost
- [] Come up with a nightly deploy script for build and test
  - [] Create a wrapper script to prevent needing to reclone trilinos or always build from scratch (maybe develop?)
- [] Come up with a clean way to deploy the environments
