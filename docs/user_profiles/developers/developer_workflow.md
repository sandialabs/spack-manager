# Quick-Start: Developer Workflow

In this section we will go over the developer work flow in Spack-Manager using the [quick-functions](https://psakievich.github.io/spack-manager/user_profiles/developers/useful_commands.html). 

This tutorial assumes you are familiar with the [3 things developers need to know](https://psakievich.github.io/spack-manager/user_profiles/developers/developer_spack_minimum.html).
If you are unfamiliar with these 3 things then please review the documentation before proceeding.

The developer workflow will be covered in 4 stages:  
1) [Setting up Spack-Manager](#setup-spack-manager)
2) [Create an environment for development](#creating-an-environment)
3) [Building and making code changes](#building-and-making-code-changes)
4) [Running tests and coming back](#running-tests-and-coming-back)

There is also the [quick start](#quick-start) below that just lists all the commands for you in a row.

## Setup Spack-Manager
Setting up Spack-Manager should be a 1 time thing on a given machine.
First pick directory you want to store Spack-Manager.
The ideal location for this directory is one that has adequate storage for multiple build environments,
and it should also be on a filesytem that is accesible where you plan to run the software.

```console
git clone --recursive git@github.com:sandialabs/spack-manager.git
```
For the purpose of this documentaiton we will define a `SPACK_MANAGER` environment variable,
and it should provide the absolute path to your Spack-Manager directory. 
Spack-Manager also provides a `spack manager location` command which will provide an absolute path 
to the Spack-Manager source directory.
To have access to the
commands we will use in this tutorial you need to source `$SPACK_MANAGER/scripts/quick_commands.sh`.
This script enables all the shell functions in Spack-Manager but it does not activate Spack.
We do this to allow you to add these lines to your `bash_profile` without any penalty
since sourcing Spack adds an unacceptable level of overhead for standard shell spawning,

```console
# These lines can be added to your bash_profile
export SPACK_MANAGER=$(pwd)/spack-manager
source $SPACK_MANAGER/scripts/quick_commands.sh
```

## Creating an Environment

With the Spack development workflow we are going to create an environment similar to a Conda environment.
Setting up the environments is a multistep process that is outlined in greater detail [here](https://sandialabs.github.io/spack-manager/user_profiles/developers/snapshot_workflow.html) and [here](https://sandialabs.github.io/spack-manager/user_profiles/developers/useful_commands.html#environment-setup-process).
There are three `quick-commands` for creating environments: `quick-create`, `quick-create-dev` and `quick-develop`.
They all exit the process of setting up an environment at different points in the process as outlined below:

| Step | quick-create | quick-create-dev | quick-develop |
|:-----|:------------:|:----------------:|:-------------:|
| Create an environment | x | x | x|
| Activate an environment | x | x | x |
| Add root specs | x | x | x|
| Add develop specs | | x | x |
| Add externals | | | x | 
| Concretize and install | | | |

For developers we recommend using `quick-create-dev` and `quick-develop` depending on if you want to use externals or not.

The interface for both of these commands is exactly the same.  Moving forward we will use `quick-create-dev` in this example.
To see the options for the command we can run it with the `--help` command.

```console
quick-create-dev -h
*************************************************************
HELP MESSAGE:
quick-create-dev sets up a developer environment
where all specs are develop specs that will be automatically cloned
from the default repos
    
The next typical steps after running this command are to add externals if
you want them, or run spack install.
    
The base command and it's help are echoed below:
    

+ spack manager create-dev-env -h
usage: spack manager create-dev-env [-h] [-m MACHINE] [-d DIRECTORY | -n NAME] [-y YAML] [-s SPEC [SPEC ...]]

optional arguments:
  -d DIRECTORY, --directory DIRECTORY
                        Directory to copy files
  -h, --help            show this help message and exit
  -m MACHINE, --machine MACHINE
                        Machine to match configs
  -n NAME, --name NAME  Name of directory for environment (managed environment)
  -s SPEC [SPEC ...], --spec SPEC [SPEC ...]
                        Specs to populate the environment with
  -y YAML, --yaml YAML  Reference spack.yaml to copy to directory
*************************************************************
```

The main flags to use for standard developer workflow are the `--name` or `--directory` flags and the `--spec` flags.

To set up a build of the exawind driver where we are developing `amr-wind` and `nalu-wind` too we would run:

```console
quick-create-dev -n example-env -s exawind@master nalu-wind@master amr-wind@main
```
If you don't want to develop one of these packages (say you're only focused on `amr-wind`) then just ommit the software you don't
plan to develop in from the spec list in the command above. Please note that these specs need to be concrete specs, meaning they have the name
(`amr-wind`) and the version from spack (`main`), and that **that the version is not necessarily the same thing as the branch**.
This is covered in the [things developers need to know about Spack](https://sandialabs.github.io/spack-manager/user_profiles/developers/developer_spack_minimum.html) for those needing a refresher.

The `-n` flag can be replaced with `-d` if we want to setup an environment in a different location than `spack:config:environments_root` (see the [spack documentation](https://spack.readthedocs.io/en/latest/config_yaml.html#spack-settings-config-yaml) for help on configuring custom managed spack environment locaitons).
The `quick-create-dev` command will execute all the stages in the table above including cloning the repos from github for the software.
These clones of the source code default to the environment directory you specified with the `-d` or `-n` flags.
If we wish to work off specific branches then we can use `git add remote`, `git fetch` and `git checkout` to get the branches we want
inside each of the clones before building.

### Managing the Source Code 

There are 4 options for setting up the source code you will use in your development process
1) Allow spack to clone the default git repo and branch when you use the `spack develop` or `spack manager develop` commands.
2) Use the `spack manager develop` command with the `--repo-branch` argument to clone from a specific fork and branch.
3) Pre-clone the source code into the environment directory.
4) Use additional `develop` arguments to point spack to exisiting source code outside the environment directory.

Option 1 happens automatically if you run `quick-create-dev`.  Option 2 can be used with an active environment.
See below for an example of how to use option2.

```console
# create an environment and acticate it with "quick-create"
# then clone the "amr-feature" branch from a user specific fork of the amr-wind git repo
# then clone the "openfast-feature" branch from a user specific fork of the openfast git repo
# finally build the software using the source code that was just cloned
quick-create -n build-from-my-fork -s amr-wind+openfast
spack manager develop --repo-branch git@github.com:psakievich/amr-wind.git amr-feature amr-wind@main
spack manager develop --repo-branch git@github.com:psakievich/openfast.git openfast-feature openfast@master
spack install
```

If you wish to pre-clone your repos using option 3 you can simply create a directory,
pre-clone the software you want to develop with names that match the package names and run your `quick-create-dev` inside the directory you created without either of the `-d` or `-n` flags.
This is because the default behavior of the command is to create the environment files, and clone repos in the current
working directory.

For example:
```console
mkdir test && cd test
# note that we name the clone of exawind-driver 'exawind' in the clone process to match the spack package name
git clone --recursive --branch main git@github.com:Exawind/exawind-driver.git exawind
git clone --recursive --branch master git@github.com:Exawind/nalu-wind.git
git clone --recursive --branch main git@github.com:Exawind/amr-wind.git
quick-create-dev -s exawind@main amr-wind@main nalu-wind@master
+ spack manager create-dev-env -s exawind@master amr-wind@main nalu-wind@master
==> Configuring spec exawind@master for development at path exawind
==> Warning: included configuration files should be updated manually [files=include.yaml]
==> Configuring spec amr-wind@main for development at path amr-wind
==> Configuring spec nalu-wind@master for development at path nalu-wind
+ spack env activate --dir /current/working/directory --prompt
```
does the same thing as 
```console
quick-create-dev -d test -s exawind@master nalu-wind@master amr-wind@main
```
However, adding in the extra pre-clone steps gives you a little more control over your environment.

Options 1 and 2 are the recommended ways of proceeding since they are the most concise and support the most common use cases.
Option 3 is available if you need additional flexibility, are on an air gaped system
or have issues with spack cloning from git (this may be due to an old version of git on the system).
Option 4 is not really recommended but the curious can learn more by diving into spack's documentation and/or using `spack manager develop --help`
to learn the features and combinations available.

At this point in the process your environment is active and all setup.
You can confirm that it is active with `spack env status` which displays the active environment.

## Building and Making Code Changes
Once the environment is setup and active you can simply run
```console
spack install
```
to build the software.

In this case we are building without externals so you will see `clingo` get bootstrapped, concretization happen, and then the install occur for the entire software stack.

You are free to make code changes in any of the code directories.
Re-running `spack install` will cause Spack to check for changes by inspecting the time-date stamp on the files in the source code directories.
If they are newer than the install time then it will trigger an incremental build to capture any changes that might exist.
Any changes you make in a dependency will also trigger a rebuild of the upstream software too.
In this environment if you make a change in `amr-wind` it will also trigger a rebuild of the `exawind` package as well.

If you wish to just do a quick incremental build you can use the `spack manager make` command:
```console
spack manager make amr-wind -j=16
```

## Running Tests and Coming Back

To run tests in a one off manner you can use the `spack build-env` command to run commands in a sub-shell with the build environment.
This is further documented [here](https://sandialabs.github.io/spack-manager/user_profiles/developers/snapshot_workflow.html#running).
We also have a function `build-env-dive` which is a beta feature that launches this same subshell in your terminal and dives into it.
It is further documented [here](https://sandialabs.github.io/spack-manager/user_profiles/developers/useful_commands.html#build-env-dive).
Finally, if a `test` target is implementd for your software you can use `spack manager make`
```console
spack manager make --args="test -j16" amr-wind
```

If you wish to come back to an environment later, or in a new shell you can just run
```console
quick-activate /path/to/the/environment/you/wish/to/activate
```
and this will do all the activation for the environment for you.
You will be able to come back at anytime and pick up where you left off.

## Quick Start
These are the commands needed to set up Spack-Manager and a development build for the exawind-driver with the intention of editing `nalu-wind` and `amr-wind` at the same time.
```console
# setup Spack-Manager
git clone --recursive git@github.com:sandialabs/spack-manager.git
export SPACK_MANAGER=$(pwd)/spack-manager
source $SPACK_MANAGER/start.sh
# setup environment
quick-create-dev -n demo -s exawind@master amr-wind@main nalu-wind@master
# build code
spack install
# code changes in amr-wind
spack cd amr-wind
# .... make code changes
# code changes in nalu-wind
spack cd nalu-wind
# ... make code changes
# re-build
spack install
# go to build directory
spack cd -b nalu-wind
# run all the overset regression tests in nalu-wind
spack build-env nalu-wind ctest -R overset
# run regression tests in the exawind-driver
build-env-dive exawind
ctest -VV
# don't forget you need to exit this build env subshell when you're done by calling `exit`
```
