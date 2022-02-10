# Developer Tutorial

In this tutorial we will look at how to setup a developer workflow using some helper scripts
provided by spack-manager.
These helper scripts are not really necessary since in the end we are just using the
[spack develop feature](https://spack-tutorial.readthedocs.io/en/latest/tutorial_developer_workflows.html).
This is just a spack environment that will build off a locally cloned copy of the package you're developing.
You can make changes to this local repo and have these changes propagate downstream to the rest
of the software stack you are developing.

If you want to skip the explanations and just run some commands to get going jump to the [quick start](#quick-start)

The advantages of using the scripts provided by spack-manager is that the configurations
you will be using will match the nightly test process for machines you are using,
and the convenience of setting things up quickly.

First to setup spack-manager execute the following commands:
```
git clone --recursive https://github.com/psakievich/spack-manager.git
export SPACK_MANAGER=$PWD/spack-manager
```

It is advisable to set `SPACK_MANAGER` environment variable in your `bashrc` or `bash_profile`
since most of the scripts rely on this environment variable to run correctly.

Next you want to activate spack via spack manager.
This can be done by sourcing the bash-script start.sh.

```
source $SPACK_MANAGER/start.sh
```

Another convenience feature you can add to your `bashrc` to help with this in the future is
```
source $SPACK_MANAGER/scripts/useful_bash_functions.sh
```
This will give you access to several useful quick functions such as
  1) `spack-start` to auto load spack for you
  2) `quick-start` to auto load spack and activate an environment whose location you pass as the first argument`

The steps up to this point have just served to activate spack in the active shell.
Next we will setup a development environment.

To do this we can use the spack-manager convenience script `create_machine_spack_environment.py`.
This script will populate a directory with the [yaml files](https://spack.readthedocs.io/en/latest/configuration.html) that will define the spack [environment](https://spack.readthedocs.io/en/latest/environments.html).
We will specify the compilers, packages and configuration settings that are going to control the build environment.
Luckily, `create_machine_spack_environment.py` will leverage the collective knowledge stored in the spack-manager repository to setup these things for you.

So to let's create the build environment. Let's assume we are on one of the Sandia ascicgpu machines and we'd like to do some work in cuda for nalu-wind.
Run the following command:

`create_machine_spack_environment.py --directory demo --spec 'nalu-wind+cuda cuda_arch=70'`

This command will create the directory `demo` and copy/create files that we need for the environment.

To activate this environment run:
```
spack env activate -d demo
```
or use the shorthand function provided by spack:
```
spacktivate demo
```
Activating an environment restricts spack's functionality to specifically what is defined
in the environment.

The file that determines the spack environment is the `spack.yaml` file which you will see in
`demo/spack.yaml`.
If you look at the contents of this file you will see:
```
spack:
  include:
  - general_packages.yaml
  - general_config.yaml
  - general_repos.yaml
  - machine_config.yaml
  - machine_packages.yaml
  - machine_compilers.yaml
  concretization: together
  view: false
  specs:
  - nalu-wind+cuda cuda_arch=70
```
The includes files are also located in the `demo` directory. 
These contain machine specific (in this case ascicgpu) and general 
configurations.
The order they are listed in also determines the level of precedence the configuration files are given.
These are copied from the machine specific configs directory stored in the
spack-manager repository.
Further details of these files are outside the scope of this tutorial but can be found
in the [spack configuration files documentation](https://spack.readthedocs.io/en/latest/configuration.html).

The spec is what we set and determines how the packages will be built (TPLS, settings, etc.).
Multiple specs can be added in a given environment but for the demo we will only have one.

Next we will create a develop spec.
Typically all of the packages that spack will install will be cached away inside spec and the 
contents of the builds are not readily available or modifiable.
However, a develop spec is one where you can control the source code location and when you make changes to it spack will do an incremental build.

We can choose to let spack clone the git repo for us by running

```
spack develop nalu-wind@master
```
This will create the directory `demo/nalu-wind` that will be a clone of
the `nalu-wind` source code.

Or we can clone the repo ourselves and tell spack where to point to for the source code
```
git clone https://github.com/Exawind/nalu-wind.git
spack develop --path nalu-wind nalu-wind@master
```

You will notice that to add a spack develop spec you need the package name (`nalu-wind`) and a version (`master`).
This tells spack what repo to clone if you are going to have spack clone it.
You may also wonder why we are using `nalu-wind` instead of `nalu-wind`.
`nalu-wind` is a package we've added in spack-manager to make it easier for developer workflow.
We've also created `amr-wind` and `exawind` packages, but the none developer versions are also acceptable.
If you have any questions about the packages or can't remember the options for the spec's you can run `spack info [package]` to get information about any package.

Now that we've added a develop spec we can concretize.
This is how spack finalizes the environment withe the requirements and constraints communicated through the `spack.yaml` file.
To concretize run:
```
spack concretize
```

Now you can install/build:

```
spack install
```

Once the build completes we can look inside the source directory where we will see a series of files
- `spack-build-out.txt`: the build output for the development package
-  `spack-build-env.txt`: the build environment used (sourcing this file will allow you to enter the exact environment used to build the software)
-  `spack-build-[hash].txt`: the build directory where the object files, and executables can be found.
## Making Changes
If you'd like to change something about the packages in your environment,
say you want to switch from a `Release` build to a `Debug` build or add a
new variant to a package, you can modify the spec's in the `spack.yaml` file.
However, if you do this you must also run
```
spack concretize -f
```

This is how you signal to `spack` that you made a change to an existing spec and need
`spack` to recreate the dependecy tree.
This will also result in new hashes for affected packages since the specs have been changed.
## Running Tests
To run regression or unit tests you need to do two things:
  1) Get to the build directory
  2) Call your testing commands in the appropriate environment

For item 1) `spack` creates a build directory with the format `spack-build-[hash]` inside
your source code directory.
You can get to this directory from anywhere by running the command
```
spack cd -b [package]
```
This command is telling `spack` to go to the build directory of the package you'd like.
It is extra helpful if you've re-concretized your environment and have build directories
from multiple hashes in your environment.

For item 2) it is importnant to remember that `spack` is building with a different environment 
from the one you used to call the `spack install` command.
The build shell has a unique environment that should be accessed to run tests.
If you wish to run tests you will need to make sure you have that environment available to
your current shell.

There are two approaches for doing this.
The first is to use a the `spack` command `spack build-env`.
This command will let you execute any command in the same environment that a package
was build with.

For example, if you wish to run the regression tests for `nalu-wind` you can run the following. 
```
spack cd -b nalu-wind 
spack build-env nalu-wind ctest [any ctest args]
```
This has the advantage of keeping your current shell unmodified, but there is some overhead
for the command you'd like to execute.

The other option is to source the environment into your current shell.
When `spack` does a build it creates a `spack-build-env.txt` file that captures the build
environment.
This is located at the same directory level as the `spack-build-[hash]` directory.
If you source this file you can run any of the build or test commands and your environment
will match the build environment.
You can also get the output of this file by running the `spack build-env` command without any arguments.
More information on that command can be found via `spack build-env -h`.
The main disadvandtage of sourcing the build envronment directly into your working shell
is that unexpected changes might occur (python or git version may change).


To do incremental builds you can re-run `spack install`, or if you've already sourced `spack-build-env.txt` then you can navigate to the build directory and re-run `ninja` or `make` like it was a manual build outside of spack.

## Quick Start

Run these commands to install spack-manager and activate it:
```
git clone --recursive https://github.com/psakievich/spack-manager.git
export SPACK_MANAGER=$PWD/spack-manager
source $SPACK_MANAGER/start.sh
```

Setup an environment on ascicgpu:
```
create_machine_spack_environment.py --directory demo --spec 'nalu-wind+cuda cuda_arch=70'
spacktivate demo
```

Add a development spec and concretize the environment:
````
spack develop nalu-wind@master
spack concretize
````
This can be any package in the software stack, and you can add multiple develop
specs into the environment.
In this case we are only going to develop `nalu-wind` using the `master` branch.

Now build:
```
spack install
```

You can now edit the files in `demo/nalu-wind` and rebuild by calling `spack install` again.
Please note that this will only allow development in `nalu-wind`.
If you wish to also develop in `trilinos` at the same time and run the `nalu-wind` tests you should also run:
```
spack develop trilinos@develop
```
to access the package with developer features for `trilinos`.
Please note there is a [bug](https://github.com/spack/spack/issues/25370) with this in `spack` right now specifcally for the `trilinos` spec.
To get around it run the command twice
```
spack develop trilinos@develop
spack develop trilinos@develop
```


If you kill this shell you can get back to development environment by calling the following commands (assuming you have set the `SPACK_MANAGER` environment variable).
```
source $SPACK_MANAGER/start.sh # activate spack
spacktivate [pathto]/demo # activate the development environment
spack install # to build
```
or if you use the `useful_bash_functions.sh`
```
quick-start [pathto]/demo
spack install
```





