# Quick-Start: Developer Workflow

In this section we will go over the developer work flow in Spack-Manager using the [quick-functions](https://psakievich.github.io/spack-manager/user_profiles/developers/useful_commands.html). 

We will cover this in 4 stages:  
1) Setting up Spack-Manager
2) Create an environment for development
3) Building and making code changes
4) Running tests and coming back

## Setup Spack-Manager
Setting up Spack-Manager should be a 1 time thing on a given machine.
First pick directory you want to store Spack-Manager.
The ideal location for this directory is one that has adequate storage for multiple build environments,
and it should also be on a filesytem that is accesible where you plan to run the software.

```console
git clone --recursive git@github.com:psakievich/spack-manager.git
```
In order for Spack-Manager to work you need to define the `SPACK_MANAGER` environment variable,
and it should provide the absolute path to your Spack-Manager directory. To have access to the
commands we will use in this tutorial you need to source `$SPACK_MANAGER/start.sh`.
This script enables all the functions in Spack-Manager but it does not activate Spack.
We do this to allow you to add these lines to your `bash_profile` without any penalty
since sourcing Spack adds an unacceptable level of overhead for standard shell spawning,

```console
# These lines can be added to your bash_profile
export SPACK_MANAGER=$(pwd)/spack-manager
source $SPACK_MANAGER/start.sh
```

## Creating an Environment

With the Spack development workflow we are going to create an environment similar to a Conda environment.
Setting up the environments is a multistep process that is outlined in greater detail [here](https://psakievich.github.io/spack-manager/user_profiles/developers/snapshot_workflow.html) and [here](https://psakievich.github.io/spack-manager/user_profiles/developers/useful_commands.html#environment-setup-process).
There are three `quick-commands` for creating environments: `quick-create`, `quick-create-dev` and `quick-develop`.
They all exit the process of setting up an environment at different points in the process as outlined below:

| Step | quick-create | quick-create-dev | quick-develop |
-------------------------------------------------------------
| spack-start | x | x | x |
| Create an environment | x | x | x|
| Activate an environment | x | x | x |
| Add root specs | x | x | x|
| Add develop specs | | x | x |
| Add externals | | | x | 

