# Spack-Manager

[Documentation](https://sandialabs.github.io/spack-manager) | [![Test Status](https://github.com/sandialabs/spack-manager/workflows/Spack-Manager%20Tests/badge.svg)](https://github.com/psakievich/spack-manager/actions)

Spack-Manager is a light-weight extension to Spack that is intended to streamline the software development and deployment cycle for individual software projects on specific machines. 

The main goals of Spack-Manager are to:

  1. Create a uniform framework for developing, testing, and deploying specific software stacks for projects across multiple platforms while utilizing Spack as much as possible.
  2. Organize Spack extensions, machine configurations, project customizations, and tools for features that are mostly project-specific, where certain necessary customizations will ultimately become generalized and merged into Spack when appropriate.
  3. A prooving ground for new commands and features that can be upstreamed to Spack

Although not strictly necessary, it is recommended that those utilizing this tool also become familiar with the features of
Spack and consult [Spack's documentation](https://spack.readthedocs.io/en/latest/).
