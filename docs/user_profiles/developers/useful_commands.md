# Useful Commands for Development

In the [developer tutorial](https://psakievich.github.io/spack-manager/user_profiles/developers/developer_tutorial.html) the granular Spack commands are shown to help youe become familiar with the process of building with Spack.
Using these commands (along with familiatization with the [spack.yaml](https://spack.readthedocs.io/en/latest/environments.html#spack-yaml)) will allow you to create a fully customized build environments. 
As a reminder, the complete, granular list of steps to setup an environment after sourcing `$SPACK_MANAGER/start.sh` are:

### Environment Setup Process
1. `spack-start`: activate Spack in your current shell
2. `spack manager create-env`: create an environment
3. `spack env activate`: activate the environment you created
4. `spack add`: add root specs to the environment
5. `spack manager develop`: setup the source code you want to edit and configure the environment to use that code
6. `spack manager external`: optional step to link your environment against pre-built binaries
7. `spack concretize`: solve the dependency graph for your environment
8. `spack install`: build the software

### Environment Loading Process
1. `spack-start`: load Spack in your current shell
2. `spack env activate`: activate an environment
3. `spack build env [package] [commands]` or `spack cd -b [spec] && bash -rcfile ../spack-build-env.txt`: run a command in the build environment or dive into the build environment in a subshell

In practice many of these commands are redundant and unneccesary for standard development workflows.
To assist with your workflow we've pre-scripted these commands in a set of _quick-commands_.
These commands are available in your shell once you've sourced `$SPACK_MANAGER/start.sh`, and provide a drop off point in the workflows based on your needs.
Information on these commands are provided below. 

## Environment setup commands
The following commands are the convenience functions for setting up a development environment.
All of these commands will exit the shell with an active Spack environment whose name will be added
to your shell prompt.
Please note that these commands are principally constructing a valid `spack.yaml` file for you in your environment,
and that file can be manipulated as needed after the commands are executed.

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


### quick-develop
`quick-develop` executes the [environment setup process](#environment-setup-process) and exits at step 7.
This command is intended to execute the entire setup process for the default development environment on a given machine.
Upon successful execution all that is required after this command is to run `spack install` since `spack install` will also perform
concretization.
The same requirement for valid concrete specs that was in [`quick-create-dev`](#quick-create-dev) applies here along with all the same constraints.

***When should I use `quick-develop`?***  
`quick-develop` should be used if you want a rapid development environment without any need for customization.
This is the fastest and least number of commands to get you started and should work for standard development needs.


