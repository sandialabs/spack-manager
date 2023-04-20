# Developers: What you need to know about Spack

Developers who are using Spack-Manager as their build system need to know some basic things about Spack 
to effectively utilize the tool.
We've tried to minimize the required knowledge you need to retain for commands, but it is important to
understand the fundamental concepts of Spack to obtain autonomy in your basic workflow and communicate
effectively when looking for help.

The most critical concepts to learn for development are:
1. [Querying the Spack commands](#querying-the-spack-commands): `spack info` and `--help`
2. [Reading and writing Spack specs](#reading-and-writing-spack-specs)
3. [The major steps of the Spack build process](#major-steps-of-the-spack-build-process)

## Querying the Spack commands

The first item in this list is also arguably the most important.
A large array of questions about Spack can be answered by simply using the `-h` or `--help` flags
for the commands.  Every Spack command has this feature and this will print a short 
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
Prints all the information you need to know about how to use the command `spack cd`.

Spack-Manager has emulated this behavior by adding the `-h`/`--help` flags to all of the commands including shell commands.
So if you see a command you don't understand, or if you ever forget the syntax for a command, the first starting point is the `-h` flag.

Along with the `-h` command, the other querying command that every developer should know is `spack info`. 
`spack info [package name]` gives you all the information for a spec.  Specifically for developers, this will tell you the versions and variants in the queried package.

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

So if you want to know how to create a debug build, you can look at this information and see:
```
build_type [RelWithDebInfo]    --         Debug, Release,         CMake build type
                                          RelWithDebInfo,         
                                          MinSizeRel                
```
This is an list spec and the available options are listed.
So adding `build_type=Debug` to the spec i.e. `amr-wind build_type=Debug` will create a debug build.
If you want to turn on `masa`, you can add `+masa`.
This will be covered in more detail in the [next section](#reading-and-writing-spack-specs) when specs are discussed. 
For this section it is sufficient to know that `spack info` is the key to knowing what you need to write to customize your builds.

## Reading and writing Spack specs

Spack specs are critical to using Spack-Manager because they are the language used to communicate the options and configurations of 
the software that is getting built.  
We provide an overview of what a spec is, and the parts that go into making a Spack spec in our 
[general documentation](https://sandialabs.github.io/spack-manager/general/spack_features.html#spack-specs), 
and an even more thorough description can be found in the 
[spack documentation](https://spack.readthedocs.io/en/latest/basic_usage.html#specs-dependencies)

A simple description of a spec for this section can be understood by looking at delimiters in a spec: `{name}@{version}%{compiler}{variants} ^{dependent specs}`.
- `name` is the package name.  This is what you query with the `spack info` and is typically the name of the software.
- `version` is what immediately follows the `@` symbol.  This can be aligned to a github branch, tag, or a url (i.e. download a tar file). The details for the versions can be found via the `spack info command`
- `compiler` specification is what immediately follows the `%` symbol, and typically also has a name and version i.e. `gcc@9.3.0`
- `variants` are the flags for the software. They can be booleans (where `+` is on and `~` is off) and lists i.e `build_type=Release` or `cuda_arch=70`
- `dependent specs` are the ways to specify flags for the dependencies.  Whenever a `^` is added it is delimiting to a new spec with the restriction that must be in the dependency graph of the first spec or _root spec_. 

We don't recommend developers use the `^` command at all since it makes things more confusing, and is unnecessary for normal development cycles.
It is addressed here for clarity and completeness, but you won't need them unless you intend to build multiple version of the same software in the same environment.
An example of this would be an environment that builds the same software with multiple compilers, but this is typically a feature for system administrators, not standard development cycles.

## Major steps of the Spack build process

Spack-Manager uses [Spack environments](https://spack.readthedocs.io/en/latest/environments.html) to manage your development builds.
These environments are similar to Conda environments in concept, but they benefit from re-using software that you've built in previous environments.
As such it is recommended that you maintain a single instance of Spack-Manager to organize and curate your builds, and create new environments when you want to start a new development project.  For example if you are working on multiple features at the same time it is convenient to maintain multiple environments.

Understanding the steps that go into creating an environment is helpful for debugging and thinking about how to organize your workflow.
Spack and Spack-Manager are also relatively easy to script in either bash or python, 
but it is important to understand the build process to write effective scripts.

The major steps and associated commands for building software with Spack environments are (don't forget to [query the commands](#querying-the-spack-commands) to learn more about them):
1. **Create the environment:** (`spack manager create-env`)  
   This generates a `spack.yaml` file which is how the environment is defined. Most of the following commands will be manipulating this file.
2. **Activate the environment:** (`spack env activate`)  
   This sets the environment as active in your shell.
3. **Add root specs:** (`spack add`)  
   Define the software that you want in the environment.  Spack will solve for the dependencies of all these root specs, and ensure that your environment meshes together. They just need the `name` as a minimum.
4. **Add develop specs** (`spack develop`)  
   Determine what software you want to modify i.e. which specs you want to develop.
   These specs must have the `name` and `version` as a minimum.
   They are not going to be added to your environment by themselves, but rather serve as keys for the concretizer to determine if a spec should be treated as a develop spec or not.
   Essentially, if the concretizer can determine that a spec in the graph can be equivalenced with the develop spec, then it will use your source code and not spack's usual process for cloning/building/installing.
   Think of this as a sort of dictionary.
   For instance `spack add trilinos` and `spack develop trilinos@develop` will mean that trilinos will use the source code,
   but if you had done `spack add trilinos@master` then it would not because `trilinos@develop` and `trilinos@master` can't be equivalenced.
   It is recommended that you always just do `name@version` for your develop specs to get the broadest match possible.
   More documentation on this can be found in the [spack documentation](https://spack-tutorial.readthedocs.io/en/latest/tutorial_developer_workflows.html).
5. **Concretize:** (`spack concretize`)  
   This is how the Spack determines what the dependency graph needs to look like for your environment.  It is a non-trivial problem to solve since you can use any combination of variants in each package in the [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph).  Each software package can enforce built in conflicts that are set by the maintainers, but anything that is not constrained by your spec or the software itself will fall to the default (once again look to `spack info` to see the defaults).
6. **Build/install:** (`spack install`)  
   Now that you've decided what combination of software you want to build, what elements you want to develop, and what the dependency graph is all that is left is to build and install. Easy right?

This may seem like a lot to go over, and this was not a very thorough description of each step.
These steps are covered with a workflow example in the [developer tutorial](https://sandialabs.github.io/spack-manager/user_profiles/developers/developer_workflow.html)
where we walk through each step one at a time. 
The intention of this page is to serve as an introduction and a reference going forward.
If you forget a step or command you can always come back to this page to see what it is and see a brief description of the whole process.
It is also important to know that in your practical workflow you won't need to type out each command every time you want to use Spack-Manager.
Spack-Manager contains convenience scripts that wrap the steps together, and print them as they execute to help you remember them.

The two most hands off commands are:

- `quick-create-dev`: this will do steps 1-5 for you automatically if you provide specs with versions in the input arguments (stops at step 4 if you don't)
- `quick-activate`: this will activate a previously created environment for you. You just pass the directory location to it.

For example, fastest way to start developing `amr-wind` and `openfast` together is:

```
quick-create-dev --name my-dev-project --spec amr-wind@main+openfast openfast@master
# go to amr-wind source code
spack cd amr-wind # modify the code in here as you wish
# go to openfast source code
spack cd openfast # modify the code in here as you wish
# install code
spack install
```

As a reminder, to learn more about the commnands used above `quick-create-dev --help`, `spack cd --help`, `spack install --help`.
To learn what other build options you have for `amr-wind` ... `spack info amr-wind`, `openfast` ... `spack info openfast`, etc.
