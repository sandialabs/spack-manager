# Developers: What you need to know about spack

Developers who are using Spack-Manager as their build system need to know some basic things 
about Spack to effectively utilize the tool.
We've tried to minimize the required knowledge you need to retain for commands, but it is important to understand the basic concepts of Spack to obtain autonomy in your basic workflow and communicate effectively when looking for help.

The most critical concepts to learn for development are:
1. [Querying the Spack commands](querying-the-spack-commands): `spack info` and `--help`
2. [Reading and writing Spack specs](reading-and-writing-spack-specs)
3. The major steps of the build process

## Querying the Spack commands

The first item in this list is also arguably the most important.  
A large array of questions about Spack can be answered by simply using the `-h` or `--help` flags
for the commands.  Every single Spack command has this feature and this will print a short 
description of the what the command does along with all the options the command takes.
For example:
```
spack cd -h
usage: spack cd [-h] [-m | -r | -i | -p | -P | -s | -S | --source-dir | -b | -e [name]] ...

cd to spack directories in the shell

positional arguments:
  spec                  package spec

optional arguments:
  --source-dir          source directory for a spec (requires it to be staged first)
  -P, --packages        top-level packages directory for Spack
  -S, --stages          top level stage directory
  -b, --build-dir       build directory for a spec (requires it to be staged first)
  -e [name], --env [name]
                        location of the named or current environment
  -h, --help            show this help message and exit
  -i, --install-dir     install prefix for spec (spec need not be installed)
  -m, --module-dir      spack python module directory
  -p, --package-dir     directory enclosing a spec's package.py file
  -r, --spack-root      spack installation root
  -s, --stage-dir       stage directory for a spec
```
Prints all the information you need to know about how to use the command `spack cd`

Spack-Manager has emulated this behavior by adding the `-h`/`--help` flags to all of the commands including shell commands.
So if you see a command you don't understand, or if you ever forget the syntax for a command, the first starting point is the `-h` flag.

Along with the `-h` command, the other querying command that every developer should know is `spack info`. 
`spack info [package name]` gives you all the information for a spec.  Specifically for developers, this will tell you the versions and variants
for the queried package.

For example `spack info amr-wind` gives:
```
spack info amr-wind
CMakePackage:   amr-wind

Description:
    None
Homepage: https://github.com/Exawind/amr-wind

Maintainers: @jrood-nrel @michaeljbrazell

Externally Detectable: 
    False

Tags: 
    ecp  ecp-apps

Preferred version:  
    main    [git] https://github.com/Exawind/amr-wind.git on branch main

Safe versions:  
    main    [git] https://github.com/Exawind/amr-wind.git on branch main

Deprecated versions:  
    None

Variants:
    Name [Default]                 When       Allowed values          Description
    ===========================    =======    ====================    ==================================

    amdgpu_target [none]           +rocm      none, gfx1011,          AMD GPU architecture
                                              gfx906, gfx802,         
                                              gfx701, gfx803,         
                                              gfx1010, gfx900,        
                                              gfx801, gfx1012,        
                                              gfx908, gfx90a          
    asan [off]                     --         on, off                 Turn on address sanitizer
    build_type [RelWithDebInfo]    --         Debug, Release,         CMake build type
                                              RelWithDebInfo,         
                                              MinSizeRel              
    clangtidy [off]                --         on, off                 Turn on clang-tidy
    cppcheck [off]                 --         on, off                 Turn on cppcheck
    cuda [off]                     --         on, off                 Build with CUDA
    cuda_arch [none]               +cuda      none, 32, 35, 10,       CUDA architecture
                                              86, 72, 62, 61, 70,     
                                              21, 50, 11, 12, 37,     
                                              52, 30, 75, 53, 60,     
                                              20, 13, 80              
    hypre [on]                     --         on, off                 Enable Hypre integration
    internal-amrex [on]            --         on, off                 Use AMRex submodule to build
    ipo [off]                      --         on, off                 CMake interprocedural optimization
    masa [off]                     --         on, off                 Enable MASA integration
    mpi [on]                       --         on, off                 Enable MPI support
    netcdf [on]                    --         on, off                 Enable NetCDF support
    openfast [off]                 --         on, off                 Enable OpenFAST integration
    openmp [off]                   --         on, off                 Enable OpenMP for CPU builds
    rocm [off]                     --         on, off                 Enable ROCm support
    shared [on]                    --         on, off                 Build shared libraries
    tests [on]                     --         on, off                 Activate regression tests
    unit [on]                      --         on, off                 Build unit tests

Installation Phases:
    cmake    build    install

Build Dependencies:
    amrex  cmake  cuda  hip  hsa-rocr-dev  hypre  llvm-amdgpu  masa  mpi  netcdf-c  openfast  py-matplotlib  py-pandas

Link Dependencies:
    amrex  cuda  hip  hsa-rocr-dev  hypre  llvm-amdgpu  masa  mpi  netcdf-c  openfast  py-matplotlib  py-pandas

Run Dependencies:
    None

Virtual Packages: 
    None
```

So if you want to know how to make it a debug build, you see:
```
build_type [RelWithDebInfo]    --         Debug, Release,         CMake build type
                                          RelWithDebInfo,         
                                          MinSizeRel                
```
which is saying `build_type=Debug` to the spec i.e. `amr-wind build_type=Debug` to get a debug build.  
If you want to turn on masa, you can add `+masa`.  
This will be covered in more detail in the [next section](reading-and-writing-spack-specs) when specs are discussed. 
For this section it is sufficient to know that `spack info` is the key to knowing what you need to write to customize your builds.

## Reading and writing Spack specs

Spack specs are critical to using Spack-Manager because they are the language used to communicate the options and configurations of 
the software that is getting built.  
We provide an overview of what a spec is, and the parts that go into making a spack spec in our 
[general documentation](https://psakievich.github.io/spack-manager/general/spack_features.html#spack-specs), 
and an even more thorough description can be found in the 
[spack documentation](https://spack.readthedocs.io/en/latest/basic_usage.html#specs-dependencies)

A simple descrption of a spec for this seciont can be understood by looking at delimiters in a spec: `{name}@{version}%{compiler}{variants} ^{dependent specs}`.
- `name` is the package name.  This is what you query with the `spack info` and is typically the name of the software.
- `version` is what immediately follows the `@` symbol.  This can be aligned to a github branch, tag, or a url (i.e. download a tar file). The details for the versions can be found via the `spack info command`
- `compiler` specification is what immediately follows the `%` symbol, and typically also has a name and version i.e. `gcc@9.3.0`
- `variants` are the flags for the software. They can be booleans (where `+` is on and `~` is off) and lists i.e `build_type=Release` or `cuda_arch=70`
- `dependent specs` are the ways to specify flags for the dependencies.  Whenever a `^` is added it is deliminating to a new spec with the restriction that is must be in the dependency graph of the first spec or _root spec_. 

We don't recommend developers use the `^` command at all since it makes things more confusing, and is unnecessary for normal development cycles.
It is addressed here for clarity and completeness, but you won't need them unless you intend to build multiple version of the same software in the 
same environment.
An example of this would be building multiple compilers, but this is typically a feature for system administrators, not standard development cycles.
