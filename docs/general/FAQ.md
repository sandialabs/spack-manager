# Frequently Asked Questions:

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

