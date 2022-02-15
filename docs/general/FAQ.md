# Frequently Asked Questions:

## What are the ^ in the specs?
^ characters in a spec such as `nalu-wind ^trilinos` are spec delimiters.  Using this character allows you to specify the details of dependencies of the root spec.  So `nalu-wind ^trilinos build_type=Debug` is saying I want to build `nalu-wind` and I want the build of Trilinos to be a debug build.

## How do I turn on an optional dependency for my software?
In spack all optional build features are called varinats. You can see what variants are available for any package (piece of software) by running the `spack info` command.  For example to build `amr-wind` with `openfast` you can see what the syntax is by typing:
`spack info amr-wind` and under the variants you will see `openfast`.  
So make your spec `amr-wind+openfast` and it will put `openfast` in the DAG and link/build for you.

## Where is my build directory/where is my install directory?
Spack manages directories by using hashes.  This is not convenient for just looking at things and knowing what they are, but it is very efficient for keeping things organized.  You can find the location of build/install with `spack location -b [spec]` for a build or `spack location -i [spec]` for the install.  Similarly, you can navigate to any directory with `spack cd -b [spec]` or `spack cd -i [spec]`.

## How do I run tests after building the software?
The first thing to understand is that spack is going to build your software in a different environment than your active shell.  To run a command in this environment you can use `spack build-env [spec] [command]` and the `[command]` will be exectued for you in the build environment (don't forget to navigate to the build directory first!).
Spack-Manager also provides a convenience function `build-env-dive [spec]` which will navigate to the build directory for you and launch a sub-shell using the build environment. You will need to type `exit` to get back to your original shell when you are done. The former is recommended for one-off commands, and the latter if you have a lot of commands to run in the environment.

So you can either: 
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