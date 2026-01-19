# Analysts Documentation

This documentation is for people who just want to run the software on preconfigured machines. 

Spack-Manager deploys software through modules. The Spack-Manager infrastructure is designed to create time-stamped snapshots. Typically this will be done by system-administrators, but anyone building software can create snapshot modules or custom modules that can be shared.

To use modules you need to add the location of the module files to your `MODULEPATH` environment variable.  These are typically stored in the `$SPACK_MANAGER/modules` directory.  You can execute the command
```
module use [path/to/modules]
```
to add the Spack generated modules to the list of available modules in your environment.

The location of these module files on the major machines are:

| Machine Name | Path |
|--------------|------|
| snl-hpc | `/projects/wind/spack-manager/modules` |
| cee | `/projects/wind/spack-manager/modules` |
| eagle | `/projects/exawind/exawind-snapshots/modules` |
