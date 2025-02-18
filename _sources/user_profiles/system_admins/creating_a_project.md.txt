# Creating and configuring a Spack-Manager Project

Spack-Manager projects are the method for organizing configuration files and package repositories
associated with a given software application.

If a pre-configred project exists then it simply has to be add to the Spack-Manager configuration file.
This section will demonstrate the process of setting up a Spack-Manager project from scratch using the 
[ExaWind application](https://github.com/Exawind/).  
This is just an example that is not going to be kept up-to-date for Exawind since it is a living, independent project.
The actual ExaWind configuration can be found [here](https://github.com/Exawind/exawind-manager/).

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
└── repos

3 directories, 0 files
```

Once the first `spack manager` command is run the project `configs` and `repos` directories get populated.
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
Now configurations can be added.
The following two configurations are used by ExaWind.

``` yaml
# config.yaml
config:
  mirrors:
    e4s: https://cache.e4s.io
```

``` yaml
# packages.yaml
packages:
  hypre:
    variants: +shared~fortran
  all:
    compiler: [apple-clang, gcc, clang]
    providers:
      mpi: [mpich, openmpi]
```

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

So any configurations in `base` are not the law and can be overridden on each machine as necessary.
An example of this would be if the project prefers to build with `+shared` but on specific platform can only support `~shared`. 
As a reminder, this hierarchy is only for creating the default environment configuration on each platform when it is created.
These are added to the `spack.yaml` via entries in the `includes` [list](https://spack.readthedocs.io/en/latest/environments.html#included-configurations).
Each environment can still be customized by modifying the `spack.yaml` file and using [additional configuration techniques](https://spack.readthedocs.io/en/latest/environments.html#configuring-environments).

For completeness, the optional `base` and `user` directories will now be added to the `exawind-demo` project.

``` console
$ mkdir $SCRATCH/exawind-demo/configs/base
$ mkdir $SCRATCH/exawind-demo/configs/user
$ spack manager find-machine --list
Project:         Machine:        Detected: (+/-)
------------------------------------------------------------
exawind-demo     darwin          -
```

The output above shows how these config directories are ignored by the `find-maachine` command.
Next we'll add some of the `base` configs used by ExaWind to the `base` directory.

``` yaml
# config.yaml
config:
  source_cache: ~/.spack_downloads
  misc_cache: $spack/../.cache
  build_stage:
    - $spack/../stage
  concretizer: clingo
```

``` yaml
# concretizer.yaml
concretizer:
  unify: false
  reuse: false
```

Now if we create an environment using `spack manager create-env --machine darwin` we will see all the configs that have been added in the `include.yaml` file.

``` console
$ spack manager create-env --machine darwin -d $SCRATCH/example-env
making /Users/psakiev/scratch/example-env

$ cat $SCRATCH/example-env/spack.yaml
# This is a Spack Environment file.
#
# It describes a set of packages to be installed, along with
# configuration settings.
spack:
  # add package specs to the `specs` list
  specs: []
  view: false
  concretizer:
    unify: true
  include:
  - include.yaml

$ cat $SCRATCH/example-env/include.yaml
concretizer:
  unify: false
  reuse: false
packages:
  hypre:
    variants: +shared~fortran
  all:
    compiler: [apple-clang, gcc, clang]
    providers:
      mpi: [mpich, openmpi]
config:
  mirrors:
    e4s: https://cache.e4s.io
  source_cache: ~/.spack_downloads
  misc_cache: $spack/../.cache
  build_stage:
  - $spack/../stage
  concretizer: clingo
```

## Configuring Machine Auto-detection

The last column from the output of `spack manager find-machine --list` indicates if the configuration
was detected for the current machine.
The default behavior is to detect nothing and require users to specify the machine they want to use.
However, setting up automatic detection is simple and highly configurable for each project and each machine.

To add detection a project must have a python file named `find-[project].py` in the top-level directory of the project (`exawind-demo` in this example).
`find-[project].py` needs to have a method named `detector` that takes a string with the machine name and returns 
`True` or `False` depending on if the current machine meets the criteria for that name.

Here is an example `find-exawind-demo.py` script

``` python
import sys

def detector(name):
    """
    A function that will check if the supplied name/machine
    matches a known machine configuration
    """
    # dictionary that is easily extensible where key is the name we want to match
    # and the value is function that can be evaluated to test the actual system we
    # are one
    known_machines = {
        "darwin": lambda: sys.platform == "darwin",
    }

    if name in known_machines:
        return known_machines[name]()
    else:
        return False
        
```

Now when the `find-machine` command is run the `darwin` machine will be detected.
``` console
$ spack manager find-machine --list
Project:         Machine:        Detected: (+/-)
------------------------------------------------------------
exawind-demo     darwin          +
```

Users are free to implement and sort of detection script they want.  
The only requirements are that the method `detector` have a positional
argument for the name of the machine to check for, and returns a boolean to indicate if that supplied name 
was detected.

## Setting up Spack Package Repositories
The `[Project]/repos` directory is a place holder for package repositories that are paired with the softwware applications development/deployment.
The simplest way to ensure the appropriate repos are included is to add a reference to them in 
`[Project]/configs/base/repos.yaml` file.
This is a way to ensure that any environment created with Spack-Manager for the desired project will include the repos.  

An example for ExaWind is as follows:
``` yaml
# repos.yaml
repos:
  - $spack/../repos/exawind
```

Where the `$spack` is a supported 
[configuration variable](https://spack.readthedocs.io/en/latest/configuration.html#config-file-variables)
that will be expanded by spack.
This works for ExaWind because ExaWind creates a fixed mirror of spack that is submoduled
into their Project repository.

Utilizing a configuration variable, environment variable, or manually updating  the repo paths are currently
the only way to point to repos in arbitrary locations on the filesystem.
Users may also add the `copy_repos: true` flag to their projects inside the `spack-manager.yaml` configuration 
file if they wish to just automatically copy the repo files locally to an environment when it is created.

``` yaml
spack-manager:
  projects:
  - $SCRATCH/exawind-demo
    copy_repos: true
```

In this case the repo specification would be properly resolved with the following `repo.yaml` file in the `base` configs.

``` yaml
# repos.yaml
repos:
  - $env/repos/exawind
```

Now when an environment is created the `[Projects]/repos` directory will be copied completely to the environment, and 
the environment will look for the copy relative to its own location.

Please note, that these are mainly small tricks to utilize spack's builtin path resolution strategies.
Additional work in the future is anticipated to make this a more seamless setup and transition.

## Adding Version Control
At this point the `exawind-demo` project is populated with an initial set of configurations.
It is highly suggested that it be placed under some form of version control.
`git` is by far the most popular tool for version control at the moment.
A suggested `.gitignore` file would look something like the following:
``` bash
# basic python files
__pycache__
*pyc
# some operations in spack-manager can currently create this directory
.tmp
```
