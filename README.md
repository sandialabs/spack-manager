# Spack-Manager

[Documentation](https://sandialabs.github.io/spack-manager) | [![Test Status](https://github.com/sandialabs/spack-manager/workflows/Spack-Manager%20Tests/badge.svg)](https://github.com/psakievich/spack-manager/actions)

Spack-Manager is a light-weight extension to Spack that is intended to streamline the software development and deployment cycle for individual software projects on specific machines. Currently this project focused on serving the needs of the [ExaWind project](https://github.com/ExaWind), but is designed and intended to serve multiple projects simultaneously in the future.

Spack is included as a submodule for now to ensure that all the systems are running the same (or close to the same) Spack version.

The main goals of Spack-Manager are to:

  1. Create a uniform framework for developing, testing, and deploying specific software stacks for projects across multiple platforms while utilizing Spack as much as possible.
  2. Organize Spack extensions, machine configurations, project customizations, and tools for features that are mostly project-specific, where certain necessary customizations will ultimately become generalized and merged into Spack when appropriate.
  3. Provide a synchronized [Spack](https://github.com/spack/spack) version across multiple machines and platforms.

Although not strictly necessary, it is recommended that those utilizing this tool also become familiar with the features of
Spack and consult [Spack's documentation](https://spack.readthedocs.io/en/latest/).
