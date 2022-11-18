# Bootstrapping

This Makefile installs compilers, mpi etc from the base system.
There are 3 environments that are chained through make: icomp (intermediate compiler), pcomps (production compilers), tpls.
Each environment's store (install tree) is separate to prevent cross contamination.

A Makefile for each envrionment is created using spack depfiles, and then they are all chained together with dependencies in the top-level Makefile.
