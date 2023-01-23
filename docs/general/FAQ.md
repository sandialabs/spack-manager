# Frequently Asked Questions:

## How do I setup and build custom branches of `amr-wind` and `openfast` together?
A simple script below is the minimum commands you need.
It is highly encouraged that users with this question review [Developers: What you need to know about Spack](https://sandialabs.github.io/spack-manager/user_profiles/developers/developer_spack_minimum.html).
A detailed guide explaining many of the other questions you are likely to encounter can be found in the [Quick-Start: Developer Workflow](https://sandialabs.github.io/spack-manager/user_profiles/developers/developer_workflow.html)
documentation.
```console
quick-create -n build-based-on-FAQ -s amr-wind+openfast
spack manager develop -rb https://github.com/[your fork]/amr-wind [your feature branch name] amr-wind@main
spack manager develop -rb https://github.com/[your fork]/openfast [your feature branch name] openfast@master
spack install
```

## What should I do if Spack Keeps failing to clone code for me on Eagle?
Eagle's default version of Git is very old and fails to do many operations.
To fix the cloning issue please make sure you have a more recent version of Git in your path.
Adding the following lines to your `bashrc` will fix the issue.
```bash
source /nopt/nrel/ecom/hpacf/env.sh
module load git
```

This is the minimum set of commands we've found to remove the problem.
The suggested modules to load are:
```bash
# HPACF Environment
source /nopt/nrel/ecom/hpacf/env.sh
module load gcc/9.3.0
module load binutils
module load git
module load python
```

## How do I build for GPU's?
If you are using a machine with a profile in Spack-Manager simply add `+cuda` or `+rocm` to your current specs.
If you are on an unsupported machine you will need to add the device architecture as well.
`spack info [spec]` will show you the options for this, and further questions will need to be addressed with your
system administrator.

## I'm getting lots of weird Spack errors, what should I do?
If you have multiple Spack instances or have recently updated spack things can get a little mangled.
For example if you have used Spack in the past or have more than one instance then both pull configs
from the `~/.spack` directory. 
This is a common source of user issues.
Please try the `sm-clean` function (available after `source $SPACK_MANAGER/start.sh`)  and see if it solves your issue.
If this doesn't work then raise/create an issue on slack/github and we will help you figure it out.

## What is Clingo and why is Spack saying it is __bootstrapping__ it?

[Clingo](https://potassco.org/clingo/) is a powerful answer-set solver that Spack uses to solve your software dependency DAG
during concretization.
Spack first tries to bootstrap the install from pre-built binaries to avoid making you build Clingo
and all of it's dependencies when you use a new instance of Spack.
If you wish to build it yourself, or are having issues with the bootstrap process you can run `spack bootstrap disable`.
There are several options here which you can learn about by running `spack bootstrap --help`.
Further information about bootstrapping can be found in the Spack documentation.

## What are the ^ in the specs?
^ characters in a spec such as `nalu-wind ^trilinos` are spec delimiters.  Using this character allows you to specify the details of dependencies of the root spec.  So `nalu-wind ^trilinos build_type=Debug` is saying I want to build `nalu-wind` and I want the build of Trilinos to be a debug build.

## How do I turn on an optional dependency for my software?
In Spack all optional build features are called varinats. You can see what variants are available for any package (piece of software) by running the `spack info` command.  For example to build `amr-wind` with `openfast` you can see what the syntax is by typing:
`spack info amr-wind` and under the variants you will see `openfast`.  
So make your spec `amr-wind+openfast` and it will put `openfast` in the DAG and link/build for you.

## Where is my build directory/where is my install directory?
Spack manages directories by using hashes.  This is not convenient for just looking at things and knowing what they are, but it is very efficient for keeping things organized.  You can find the location of build/install with `spack location -b [spec]` for a build or `spack location -i [spec]` for the install.  Similarly, you can navigate to any directory with `spack cd -b [spec]` or `spack cd -i [spec]`.

## How do I run tests after building the software?
The first thing to understand is that Spack is going to build your software in a different environment than your active shell.  To run a command in this environment you can use `spack build-env [spec] [command]` and the `[command]` will be exectued for you in the build environment (don't forget to [navigate to the build directory](#where-is-my-build-directorywhere-is-my-install-directory) first!).
Spack-Manager also provides a convenience function `build-env-dive [spec]` which will navigate to the build directory for you and launch a sub-shell using the build environment. You will need to type `exit` to get back to your original shell when you are done. The former is recommended for one-off commands, and the latter if you have a lot of commands to run in the environment.

Please note that 
```
spack build-env nalu-wind ctest -R ablNeutral
```
and
```
build-env-dive nalu-wind
ctest -R ablNeutral
exit
```
are equivalent.

> **Note**: When running the tests through `ctest`, it is the developer's responsibility to ensure that the gold files, located in `${SPACK_MANAGER}/golds/current`, have been populated. This can typically be done by copying the gold files from `${SPACK_MANAGER}/golds/tmp` (generated from an initial `ctest` run). For example, populating the gold files for Nalu-Wind for Linux entails:
```
cp -r ${SPACK_MANAGER}/tmp/nalu-wind/Linux ${SPACK_MANAGER}/golds/current/nalu-wind/
```

## Should I worry about _Warning: included configuration files should be updated manually_?
No, this is just a warning from Spack saying it won't automatically update the custom files we've created
for dialing in machine specific data for your environment `include.yaml` or the list of externals we're using
to provide pre-compiled binaries for you to link against `externals.yaml`.

## Should I worry abour _Warning: the original concretizer is currently being used._?
No, we are using the original concretizer when you use externals from snapshots as a stop gap until
the Spack team fixes a bug for us.

## How do I use the executables I built in my development environment?
You need to activate the environment `quick-activate`, and then call `spack load [package]`.
This will load the binaries you need into your `$PATH`.
```
# Example
quick-activate $SPACK_MANAGER/environments/exawind
spack load amr-wind
mpirun -np 20 amr_wind -i [foo]
```

## What to do about _Error: Couldn't find patch for package exawind.hdf5_?
Please let us know if you see this. We are trying to make sure you don't see it.
To get rid of the error run `spack clean -m`

## I'm getting an error saying there is a missing variant? _Error: variant [foo] not found ..._
Typically this means your Spack submodule is out of date.  To check run
```
cd $SPACK_MANAGER
git status
```
If you see `spack` in there then you need to re-sync the submodule. `git submodule update` etc

## Permissions issues on NREL's Eagle machine: __[Errno 13] Permission denied:__ 
To build successfully on Eagle, in general you want the following in your `.bashrc` to avoid issues with `tmp` directories:
```
mkdir -p /scratch/${USER}/.tmp && export TMPDIR=/scratch/${USER}/.tmp
```

## How do I compile faster using a parallel DAG?
The `spack install` command gives you parallel builds inside each `make` command. However, further parallelism can be had on large DAGs by invoking concurrent `spack install` commands. Spack will find parallelism within the DAG and build any packages it can simultaneously using file locks. You can do this in bash with the following command:
```
for i in {1..4}; do nice spack install & done; wait
```
If you have really large DAGs, it's even possible to use `srun` on multiple nodes for the install process.

Another newer method for this in Spack is to use depfiles where Spack can generate standard makefiles which can expose the DAG parallelism. More documentation on this can be found [here](https://spack.readthedocs.io/en/latest/environments.html#generating-depfiles-from-environments). In summary, once you have an environment concretized you can generate a makefile and replace the `spack install` with a `make` command as such:
```
spack -e . env depfile -o Makefile
make -j8
```
