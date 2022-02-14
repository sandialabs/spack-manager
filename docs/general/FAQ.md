# Frequently Asked Questions:

## What are the ^ in the specs?
^ characters in a spec such as `nalu-wind ^trilinos` are spec delimiters.  Using this character allows you to specify the details of dependencies of the root spec.  So `nalu-wind ^trilinos build_type=Debug` is saying I want to build `nalu-wind` and I want the build of Trilinos to be a debug build.

## How do I turn on an optional dependency for my software?
In spack all optional build features are called varinats. You can see what variants are available for any package (piece of software) by running the `spack info` command.  For example to build `amr-wind` with `openfast` you can see what the syntax is by typing:
`spack info amr-wind` and under the variants you will see `openfast`.  
So make your spec `amr-wind+openfast` and it will put `openfast` in the DAG and link/build for you.