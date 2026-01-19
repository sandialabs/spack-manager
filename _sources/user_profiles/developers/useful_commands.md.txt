# Useful Commands for Development

In the [developer tutorial](https://sandialabs.github.io/spack-manager/user_profiles/developers/developer_tutorial.html) the granular Spack commands are shown to help youe become familiar with the process of building with Spack.
Using these commands (along with familiarization with the [spack.yaml](https://spack.readthedocs.io/en/latest/environments.html#spack-yaml)) will allow you to create a fully customized build environments. 

In practice many of these commands are redundant and unneccesary for standard development workflows.
To assist with your workflow we've pre-scripted these commands in a set of _quick-commands_.
These commands are available in your shell once you've sourced `$SPACK_MANAGER/scripts/quick_commands.sh`, and provide a drop off point in the workflows based on your needs.
All of the _quick-commands_ will echo all the calls to spack (pre-pended with a `+ ` ) so you can see what is being called and can reproduce them execution outside these scripts as needed.

Information on these commands are provided below. 

For a quick reference: the commands that are anticipated to be the most commonly used are:
- [`quick-develop`](#quick-develop)
- [`quick-activate`](#quick-activate)
- [`build-env-dive`](#build-env-dive)

## Environment setup process
As a reminder, the complete, granular list of steps to setup an environment after sourcing `$SPACK_MANAGER/start.sh` are:
1. `spack manager create-env`: create an environment
2. `spack env activate`: activate the environment you created
3. `spack add`: add root specs to the environment
4. `spack manager develop`: setup the source code you want to edit and configure the environment to use that code
5. `spack manager external`: optional step to link your environment against pre-built binaries
6. `spack concretize`: solve the dependency graph for your environment
7. `spack install`: build the software

## Environment loading process
The complete, granular list of steps to re-use an environment after sourcing `$SPACK_MANAGER/start.sh` are:
1. `spack env activate`: activate an environment
2. `spack build env [package] [commands]` or `spack cd -b [spec] && bash -rcfile ../spack-build-env.txt`: run a command in the build environment or dive into the build environment in a subshell

## Environment setup commands
The following commands are the convenience functions for setting up a development environment.
All of these commands will exit the shell with an active Spack environment whose name will be added
to your shell prompt.
Please note that these commands are principally constructing a valid `spack.yaml` file for you in your environment,
and that file can be manipulated as needed after the commands are executed.

(#quick-create)=
### quick-create
`quick-create` executes the [environment setup process](#environment-setup-process) and exits at step 4.
If you supply specs with the `--spec` or `-s` flag then those will be added as root specs and you can effectively be at step 5
`spack manager develop`.

***When should I use `quick-create`?***  
This command should be used by individuals who want to have control over the git clone process and/or locations of the source code
they are intending to develop.
`spack manager develop` gives you the abiilty to point to pre-cloned code, or to select the fork and branch you want to clone from.
If these are desirable features then you will need to run the remaining steps of the [environment setup process](#environment-setup-process)
manually.

(#quick-create-dev)=
### quick-create-dev
`quick-create-dev` executes the [environment setup process](#environment-setup-process) and exits at step 5.
If you supply concrete specs, which means they have the name and version (i.e. `amr-wind@main`), then `spack-manager develop` will be called for you
and the default repos/branches will be cloned to the environment directory for you.
If you fail to supply a concrete spec then this command will give a warning letting you know the spec wasn't concrete, and the behavior will stop at step 4.
In other words it will behave exactly like [`quick-create`](#quick-create).

***When should I use `quick-create-dev`?***  
`quick-create-dev` should be used if you don't mind accepting the default repo cloning, but need to specifiy the externals you will link against
with `spack manager external` or if you don't want to use externals at all.
A common scenario for this is if you are building with the non-standard view that you can see from `spack manager external --list`.
The first view listed in the parenthesis for the latest timestamped snapshot is the default. 
If this one doesn't match your build needs then you will need to specifiy the correct one manually.

(#quick-develop)=
### quick-develop
`quick-develop` executes the [environment setup process](#environment-setup-process) and exits at step 7.
This command is intended to execute the entire setup process for the default development environment on a given machine.
Upon successful execution all that is required after this command is to run `spack install` since `spack install` will also perform
concretization.
The same requirement for valid concrete specs that was in [`quick-create-dev`](#quick-create-dev) applies here along with all the same constraints.

***When should I use `quick-develop`?***  
`quick-develop` should be used if you want a rapid development environment without any need for customization.
This is the fastest and least number of commands to get you started and should work for standard development needs.

## Environment re-use commands
These commands are designed to help you efficiently re-use an environment that has already been setup.

(#quick-activate)=
### quick-activate
`quick-activate` executes the first two steps of the [environment loading process](#environment-loading-process)
i.e. `spack-start && spack env activate`.
To use it you simply pass the directory path to the environment you wish to activate i.e. `quick-activate $SPACK_MANAGER/environments/exawind`
and it will activate the environment and add the name of the environment to your shell prompt.

***When should I use `quick-activate`?***  
Whenever you want to come back to an environment in a new shell.
There are really no down-sides to this command unless you don't like the environment name being added to your prompt.

(#build-env-dive)=
### build-env-dive
`build-env-dive` takes a spec as an argument and will move you to the location of the build directory for that spec and launch a sub-shell using the spec's build environment.
This command allows developers to work as if they had built the software manually outside of spack.
You can call `make`, `make clean`, `make install`, `ctest` etc.
Simply type `exit` to return to your original shell where you called `build-env-dive`.
It should be cautioned that diving into this environment can do things like change the version of git/python in your shell.
Also if you are doing a multi-compnent simply calling `make` will not update the entire stack like `spack install` will.

***When should I use `build-env-dive`?***
This command is most effective when you are just iterating on one software component and need to keep executing commands in that environment.
For a one off like checking a test `spack build-env [spec] [command]` is probably more efficient, but it is also clunkier to use.
In general `build-env-dive` command should be used freely as long as you are okay with it moving you to directories and are aware of the
potential issues related to opening a sub-shell with potentially different configurations.
In practice this has not been much of an issue.

## Other Commands

(#remove-spack-prompt)=
### remove-spack-prompt
This command takes no arguments unless you pass `-h` or `--help`.
It simply removes the prompt with the environment name that the _quick-commands_ add.
