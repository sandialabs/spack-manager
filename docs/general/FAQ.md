# Frequently Asked Questions:

### What are the ^ in the specs?
^ characters in a spec such as `nalu-wind ^trilinos` are spec delimiters.  Using this character allows you to specify the details of dependencies of the root spec.  So `nalu-wind ^trilinos build_type=Debug` is saying I want to build `nalu-wind` and I want the build of Trilinos to be a debug build.