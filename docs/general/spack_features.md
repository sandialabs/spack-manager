# Important Spack Features

## Spack Specs

In Spack the idea of a _spec_ is very important. Specs are descriptors of particular aspects or configurations of a package or packages.
Specs can completely general, merely denoted the name of a package, or they can very specific such as specifying the name of the package with a particular version, with a particular compiler and compiler version, with specific options called _variants_, as well as constraints on dependencies of the package.
Spack's documentation has much more information on specs [here](https://spack.readthedocs.io/en/latest/basic_usage.html#specs-dependencies), but we summarize them here as it is important to utilizing Spack.
Specs are a loose or general form of a configuration for a package. However, Spack is very exact it how it will build and satisfy your requested spec.
It does this through the process of _concretization_. Concretization maps a spec, no matter how general or specific, into an _exact_ graph of
how Spack will build and fulfill the spec. A command for understanding this process is the `spack spec` command. Using `spack spec`
will report to the user how Spack will create a concrete graph or DAG of the package on its dependencies. For example:

```
% spack spec zlib                                                  
Input spec
--------------------------------
zlib

Concretized
--------------------------------
zlib@1.2.11%apple-clang@12.0.0+optimize+pic+shared arch=darwin-catalina-skylake
```

Here we intend to install the zlib package which has no dependencies. If we specify nothing but `zlib`, this is the configuration Spack has solved
in which it will fulfill the installation of zlib. We can be more specific about our request. Looking at what compilers are available for us in Spack
we can use:
```
% spack compilers
==> Available compilers
-- apple-clang catalina-x86_64 ----------------------------------
apple-clang@12.0.0

-- gcc catalina-x86_64 ------------------------------------------
gcc@11.2.0
```

Here we are on a MacOS computer and we have two compilers available. If I prefer `zlib` be installed using gcc, one can use:
```
% spack spec zlib%gcc
Input spec
--------------------------------
zlib%gcc

Concretized
--------------------------------
zlib@1.2.11%gcc@11.2.0+optimize+pic+shared arch=darwin-catalina-skylake
```

Notice Spack honored our compiler constraint request. Spack reports the concretized spec in a manner that continues to itself be a spec:
```
% spack spec zlib@1.2.11%gcc@11.2.0+optimize+pic+shared arch=darwin-catalina-skylake
Input spec
--------------------------------
zlib@1.2.11%gcc@11.2.0+optimize+pic+shared arch=darwin-catalina-skylake

Concretized
--------------------------------
zlib@1.2.11%gcc@11.2.0+optimize+pic+shared arch=darwin-catalina-skylake
```

Therefore using the `spec` command helps us to understand specs and what Spack will do with a spec before we use them in other commands.
Here is an example of a more complicated package:
```
% spack spec amr-wind
Input spec
--------------------------------
amr-wind

Concretized
--------------------------------
amr-wind@main%apple-clang@12.0.0~cuda~fortran+hypre+internal-amrex~ipo~masa+mpi+netcdf~openfast~openmp~rocm+shared+tests+unit build_type=Release arch=darwin-catalina-skylake
    ^cmake@3.22.2%apple-clang@12.0.0~doc+ncurses+openssl+ownlibs~qt build_type=Release arch=darwin-catalina-skylake
        ^ncurses@6.2%apple-clang@12.0.0~symlinks+termlib abi=none arch=darwin-catalina-skylake
            ^pkgconf@1.8.0%apple-clang@12.0.0 arch=darwin-catalina-skylake
        ^openssl@1.1.1m%apple-clang@12.0.0~docs certs=system arch=darwin-catalina-skylake
            ^perl@5.34.0%apple-clang@12.0.0+cpanm+shared+threads arch=darwin-catalina-skylake
                ^berkeley-db@18.1.40%apple-clang@12.0.0+cxx~docs+stl patches=b231fcc4d5cff05e5c3a4814f6a5af0e9a966428dc2176540d2c05aff41de522 arch=darwin-catalina-skylake
                ^bzip2@1.0.8%apple-clang@12.0.0~debug~pic+shared arch=darwin-catalina-skylake
                    ^diffutils@3.8%apple-clang@12.0.0 arch=darwin-catalina-skylake
                        ^libiconv@1.16%apple-clang@12.0.0 libs=shared,static arch=darwin-catalina-skylake
                ^gdbm@1.19%apple-clang@12.0.0 arch=darwin-catalina-skylake
                    ^readline@8.1%apple-clang@12.0.0 arch=darwin-catalina-skylake
                ^zlib@1.2.11%apple-clang@12.0.0+optimize+pic+shared arch=darwin-catalina-skylake
    ^hypre@2.23.0%apple-clang@12.0.0~complex~cuda~debug+int64~internal-superlu~mixedint+mpi~openmp+shared~superlu-dist~unified-memory arch=darwin-catalina-skylake
        ^netlib-lapack@3.9.1%apple-clang@12.0.0~external-blas~ipo+lapacke+shared~xblas build_type=Release arch=darwin-catalina-skylake
        ^openmpi@4.1.2%apple-clang@12.0.0~atomics~cuda~cxx~cxx_exceptions+gpfs~internal-hwloc~java~legacylaunchers~lustre~memchecker~pmi~pmix+romio~singularity~sqlite3+static~thread_multiple+vt+wrapper-rpath fabrics=none schedulers=none arch=darwin-catalina-skylake
            ^hwloc@2.7.0%apple-clang@12.0.0~cairo~cuda~gl~libudev+libxml2~netloc~nvml~opencl~pci~rocm+shared arch=darwin-catalina-skylake
                ^libxml2@2.9.12%apple-clang@12.0.0~python arch=darwin-catalina-skylake
                    ^xz@5.2.5%apple-clang@12.0.0~pic libs=shared,static arch=darwin-catalina-skylake
            ^libevent@2.1.12%apple-clang@12.0.0+openssl arch=darwin-catalina-skylake
            ^openssh@8.8p1%apple-clang@12.0.0 arch=darwin-catalina-skylake
                ^libedit@3.1-20210216%apple-clang@12.0.0 arch=darwin-catalina-skylake
    ^netcdf-c@4.7.4%apple-clang@12.0.0~dap~fsync~hdf4~jna+mpi+parallel-netcdf+pic+shared patches=2c88dfbd6d339a0336a43b14a65a1d1df995b853b645e4af612617612a642a53 arch=darwin-catalina-skylake
        ^hdf5@1.10.7%apple-clang@12.0.0+cxx~fortran+hl~ipo~java+mpi+shared~szip~threadsafe+tools api=default build_type=RelWithDebInfo patches=2a1e3118d7d3d7411820e567b03530de96a46385304017f8e548408aa1cfbfc0 arch=darwin-catalina-skylake
        ^m4@1.4.19%apple-clang@12.0.0+sigsegv patches=9dc5fbd0d5cb1037ab1e6d0ecc74a30df218d0a94bdd5a02759a97f62daca573,bfdffa7c2eb01021d5849b36972c069693654ad826c1a20b53534009a4ec7a89 arch=darwin-catalina-skylake
            ^libsigsegv@2.13%apple-clang@12.0.0 arch=darwin-catalina-skylake
        ^parallel-netcdf@1.12.2%apple-clang@12.0.0~burstbuffer+cxx+fortran+pic+shared arch=darwin-catalina-skylake
```

It is obvious concretized specs can get large quite quickly. However, Spack is very good at standing on it's own without requirements
from the existing system. Therefore it can be quite straightforward to build complicated packages on many machines. However, it can also be argued
that this situation involves many packages with Spack will build that may already exist on the machine. While this is fair, we typically solve
this by specifying `externals` which make Spack aware of packages already existing on the system and utilizing them in its DAG. Spack-manager
has machine-specific configurations provided by its contributors for this purpose. Obtaining a configuration for Spack for the specific machine
and specific project will save the user of Spack a lot of time.

In our previous concretized DAG, `amr-wind` has dependencies on packages. Dependencies in specs are denoted with `^`. We can use this to constrain dependencies we would like to request.
For example here we put a constraint on the cmake version:
```
% spack spec amr-wind ^cmake@3.17.0
Input spec
--------------------------------
amr-wind
    ^cmake@3.17.0

Concretized
--------------------------------
amr-wind@main%apple-clang@12.0.0~cuda~fortran+hypre+internal-amrex~ipo~masa+mpi+netcdf~openfast~openmp~rocm+shared+tests+unit build_type=Release arch=darwin-catalina-skylake
    ^cmake@3.17.0%apple-clang@12.0.0~doc+ncurses+openssl+ownlibs~qt build_type=Release patches=1c540040c7e203dd8e27aa20345ecb07fe06570d56410a24a266ae570b1c4c39,bf695e3febb222da2ed94b3beea600650e4318975da90e4a71d6f31a6d5d8c3d,e51119dd387aa3eb2f21fee730d3aa8b5480301c5e2e3a33bd86f4f7d8903861 arch=darwin-catalina-skylake
        ^ncurses@6.2%apple-clang@12.0.0~symlinks+termlib abi=none arch=darwin-catalina-skylake
...
```
Concretization is an NP-hard problem, so solving the DAG is not instantaneous, and it is very much an active area of research. Spack has
gone through one iteration thus far of updating its concretization strategy. This is the difference between the "original" concretizer and the newer clingo concretizer.

Another important idea in Spack is describing the configuration of a particular package involving a complicated DAG into a succint string for the installation directory of the package for example. To do this, Spack collapses several properties of the DAG into a _hash_. Spack then uses this hash to provide a short form mapping for a particular package and its full description. Spack is a very powerful database of software installations and can be queried to understand the exact state of each package and pinpointing a specific package in which the user is interested. We leave these to the Spack documentation to continue.


## Spack Commands

Spack has many commands, many of which have great information when adding `-h` to them. Here we list a few of the most important commands for using within Spack-Manager.

  - `spack spec -I <spec> `: solve the DAG for the spec and show packages in the DAG that are already installed
  - `spack location -i <spec> `: used for finding the specific location of an installed package
  - `spack concretize -f `: force an activated environment to undergo concretization
  - `spack install `: install all packages listed in an environment's `spack.yaml` file
  - `spack uninstall <spec>`: uninstall specific spec
  - `spack uninstall --dependencies -a -y <spec>`: uninstall everything related to a general spec (`-a`) and all its dependencies without confirming
  - `spack cd -b <spec> `: change to build directory of package
  - `spack env activate -d <path> ` or `spacktivate -d <path>`: activate a Spack environment at specified path
  - `spack develop <spec> `: develop source code in a package locally
  - `spack help --all `: list all available Spack commands
  - `spack list <string>`: list all available Spack packages matching the string
  - `spack find <spec>`: query Spack's database of installed packages
  - `spack find -Lvd <spec>`: list the hashes, variants, and dependencies of the provided spec
  - `spack stage <spec> && spack cd <spec>`: download the package's source code and extract it for browsing
  - `spack docs`: open the online spack documentation in a browser
  - `spack -d <spack subcommand>`: get debug info on exactly what Spack is doing when it fails
  - `spack config blame packages`: show exactly where Spack is obtaining its preferences for things like concretization
  - `spack compilers`: list the compilers in which Spack is aware


## Spack Knowledgebase

In each package installation directory in `spack/opt` Spack keeps a `.spack` directory which contains information on exactly how the package was built.
