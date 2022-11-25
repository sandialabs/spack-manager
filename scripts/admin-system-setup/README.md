# Bootstrapping

This Makefile installs compilers, mpi etc from the base system.
There are 3 environments that are chained through make: bootstrap (intermediate compiler), compilers (production compilers), packages.
Each environment's store (install tree) is separate to prevent cross contamination.

A Makefile for each envrionment is created using spack depfiles, and then they are all chained together with dependencies in the top-level Makefile.

To make sure a clean environment is used when running this I used:

```
env -i bash --no-profile
```

since I have built a lot of otherthings with different spack installations
Unfortunately this can cause issues with binutils that requires, manually adding binutils to `compilers:compiler:environment:prepend_path:PATH`
or adding it to your  `PATH` before calling spack install.

This is something that should be automated in the future.
