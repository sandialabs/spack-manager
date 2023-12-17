# Creating and configuring a Spack-Manager Project

Spack-Manager projects are the method for organizing configuration files and package repositories
associated with a given software application.

If a pre-configred project exists then it simply has to be add to the Spack-Manager configuration file.
This section will demonstrate the process of setting up a Spack-Manager project from scratch using the 
[ExaWind application](https://github.com/Exawind/).  
This is just an example that is not going to be kept up-to-date for Exawind since it is a living, independent project.
The actual ExaWind configuration can be found at `TODO: Link`.

## Creating a Project from Scratch

A Project is really just a collection of directories and couple of optional python files.
In the `spack-manager.yaml` configuration file paths are provided to the projects that this instance of 
Spack-Manager is supporting.

``` console
$ cat spack-manager/spack-manager.yaml

spack-manager:
    projects:
    - $SCRATCH/exawind-demo

$ ls -lh $SCRATCH/exawind-demo
ls: /Users/psakiev/scratch/exawind-demo: No such file or directory
```

If a non-existent path is added to the `Projects` list in the `spack-manager/spack-manager.yaml` file 
then these initial directories will automatically be created the first time a `spack manager` command is run.
It should also be noted that the autocompletion of variables inside these paths (such as the `$SCRATCH` environment 
variable in this example, follow the same [variable conventions](https://spack.readthedocs.io/en/latest/configuration.html#config-file-variables) utilized by Spack. 
This is because Spack-Manager is importing and using the Spack code for these operations.

``` console
$ spack manager find-machine --list
Project:         Machine:        Detected: (+/-)
------------------------------------------------------------

$ tree $SCRATCH/exawind-demo
/Users/psakiev/scratch/exawind-demo
├── configs
└── repo

3 directories, 0 files
```

Once the first `spack manager` command is run the project `configs` and `repo` directories get populated.
The `configs` directory is where machine specific spack configuration files are stored. 
Since this directory is currently empty no machines show up when `spack manager find-machine --list` is run.
The next step is to add some machines and configuration files.
Note that __machines__ is a loose term, and it is really a bifurcation of configurations.
The term __machine__ was selected since application projects typically have to tweak their spack configurations
on each new machine/platform.

## Populating Machine Specific Configurations
Directories within the project's `configs` directory will be delineated by their names.
Let's add a directory named `darwin` inside the `configs` directory and re-run `spack manager find-machine --list`.

``` console
$ mkdir $SCRATCH/exawind-demo/configs/darwin
$ spack manager find-machine --list
Project:         Machine:        Detected: (+/-)
------------------------------------------------------------
exawind-demo     darwin          -
```

`darwin` is automatically picked up as an available machine by the `find-machine` command, and any configuration files that 
are added inside this directory will be added to an environment created with a `darwin` machine specified.
It should also be noted that the project name `exawind-demo` comes from the name of the parent directory.
Spack-Manager specific constructs are associated with the directory names they are in as much as possible to reduce the need
for in memory variables and extra book keeping. 
The filesystem is a sufficient bookkeeper for the operations Spack-Manager performs.

### Anonymous Machines
There are two anonymous machines that are reserved for project and users to utilize: `base` and `user`.
The `configs/base` directory is designed to hold project wide configurations that are the defaults utilized by every environment.
For example, the software project has non-default package variants they wish to use uniformly across all platforms these could 
be set in the `configs/base/packages.yaml` file. 

The `configs/users` directory is one that allows users to set their own personal preferences or make tweaks before pushing them
to the whole team.  An example here is if one user really prefers a specific flavor of MPI and the software project is not constrained
then they could configure that in the `configs/user/packages.yaml` file.

The hierarchy of precedent for these configs are:
1. `user`
2. `machine`
3. `base`
where the smaller number means higher precedent.

So a things in `base` are not the law and can be overridden on each machine as necessary.
An example of this would be if the project prefers to build with `+shared` but on specific platform can only support `~shared`. 
As a reminder, this hierarchy is only for creating the default environment configuration on each platform when it is created.
These are added to the `spack.yaml` via entries in the `includes` [list](https://spack.readthedocs.io/en/latest/environments.html#included-configurations).
Each environment can still be customized by modifying the `spack.yaml` file and using [additional configuration techniques](https://spack.readthedocs.io/en/latest/environments.html#configuring-environments).


## Configuring Machine Auto-detection

## Setting up Spack Package Repositories

## Adding Version Control
