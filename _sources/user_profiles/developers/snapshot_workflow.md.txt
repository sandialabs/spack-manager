# Snapshot Developer Workflow Example

**WARNING:** This documentation is fairly specific to ExaWind and has not been generalized for an arbitrary `Spack-Manager` project.
THe information is still useful. However, you may not translate directly or be able to follow along.


In this tutorial we will look at how to setup a developer workflow using snapshots if they are provided on your machine.

## Setup

We use the Eagle machine at NREL for the example, and we choose to develop both the `hypre` and `nalu-wind`
projects for running on the GPU using CUDA. Starting from nothing, we first clone Spack-Manager:
```
[user@el1 ~]$ export SCRATCH=/scratch/${USER}
[user@el1 ~]$ cd ${SCRATCH}
[user@el1 user]$ git clone --recursive https://github.com/sandialabs/spack-manager.git
Cloning into 'spack-manager'...
remote: Enumerating objects: 2610, done.
remote: Counting objects: 100% (2610/2610), done.
remote: Compressing objects: 100% (1001/1001), done.
remote: Total 2610 (delta 1345), reused 2476 (delta 1256), pack-reused 0
Receiving objects: 100% (2610/2610), 426.10 KiB | 4.14 MiB/s, done.
Resolving deltas: 100% (1345/1345), done.
Submodule 'spack' (https://github.com/spack/spack) registered for path 'spack'
Cloning into '/lustre/eaglefs/scratch/user/spack-manager/spack'...
remote: Enumerating objects: 354065, done.
remote: Total 354065 (delta 0), reused 0 (delta 0), pack-reused 354065
Receiving objects: 100% (354065/354065), 155.14 MiB | 22.08 MiB/s, done.
Resolving deltas: 100% (150589/150589), done.
Submodule path 'spack': checked out '3576e5f3d6b34d8bc8c8c8f2749127ece1ce89be'
```

We then activate Spack-Manager:
```
[user@el1 user]$ export SPACK_MANAGER=${SCRATCH}/spack-manager && source ${SPACK_MANAGER}/start.sh && spack-start
```

Once Spack-Manager itself is activated, we create the Spack environment in which we will install and develop. 
To do this we use the `spack manager create-env` command.
Our environment will be called `exawind` using the `--name` argument. We will choose to focus on building Nalu-Wind using the spec
`nalu-wind@master+hypre+cuda  %gcc`, which means, `nalu-wind` at the `master` branch, with hypre
enabled (`+hypre`), and CUDA (`+cuda `), using the GCC compiler (`%gcc`, which without a version, selects the default compiler version).
```
[user@el1 user]$ spack manager create-env --name exawind --spec 'nalu-wind@master+hypre+cuda  %gcc'
making /scratch/user/spack-manager/environments/exawind
```

Once the environment is created, we need to activate it:
```
[user@el1 user]$ spack env activate -d ${SPACK_MANAGER}/environments/exawind
```
Both of the previous steps can be combined into one with `quick-create-env -n exawind -s 'nalu-wind@master+hypre+cuda %gcc'`.

Next, we will turn `nalu-wind` and `hypre` into "develop specs" with a command that tells Spack we want to edit the code for these packages
locally and always rebuild with our local clones of the packages. We do this with the `spack manager develop` command:
```
[user@el1 user]$ spack manager develop nalu-wind@master; spack manager develop hypre@develop
==> Configuring spec nalu-wind@master for development at path nalu-wind
==> Warning: included configuration files should be updated manually [files=externals.yaml, include.yaml]
==> Configuring spec hypre@develop for development at path hypre
==> Warning: included configuration files should be updated manually [files=externals.yaml, include.yaml]
```

The `develop` command clones both of our packages into the `${SPACK_MANAGER}/environments/exawind` directory. It is possible to specify other locations
of these package repos if they are already cloned by using the `-p` option for specifying a path. If we want to let Spack clone, we 
can always switch our remotes and branches within the repos cloned by Spack by doing something like the following:
```
[user@el1 user]$ cd ${SPACK_MANAGER}/environments/exawind/nalu-wind
[user@el1 nalu-wind]$ git remote -v
origin	git@github.com:Exawind/nalu-wind.git (fetch)
origin	git@github.com:Exawind/nalu-wind.git (push)
[user@el1 nalu-wind]$ git remote add mine git@github.com:user-nrel/nalu-wind.git
[user@el1 nalu-wind]$ git remote rm origin
[user@el1 nalu-wind]$ git remote rename mine origin
[user@el1 nalu-wind]$ git pull
remote: Enumerating objects: 15, done.
remote: Counting objects: 100% (14/14), done.
remote: Compressing objects: 100% (4/4), done.
remote: Total 15 (delta 10), reused 14 (delta 10), pack-reused 1
Unpacking objects: 100% (15/15), 2.78 KiB | 237.00 KiB/s, done.
From github.com:user-nrel/nalu-wind
 * [new branch]        jroverf/NonTemplateNodalGradPOpenBC -> origin/jroverf/NonTemplateNodalGradPOpenBC
 * [new branch]        master                              -> origin/master
 * [new branch]        update_golds_10_26_2021             -> origin/update_golds_10_26_2021
There is no tracking information for the current branch.
Please specify which branch you want to merge with.
See git-pull(1) for details.

    git pull <remote> <branch>

If you wish to set tracking information for this branch you can do so with:

    git branch --set-upstream-to=origin/<branch> master

[user@el1 nalu-wind]$ git branch --set-upstream-to=origin/master master
Branch 'master' set up to track remote branch 'master' from 'origin'.
[user@el1 nalu-wind]$ git pull
Already up to date.
[user@el1 nalu-wind]$ git checkout update_golds_10_26_2021

Branch 'update_golds_10_26_2021' set up to track remote branch 'update_golds_10_26_2021' from 'origin'.
Switched to a new branch 'update_golds_10_26_2021'
[user@el1 nalu-wind]$ git branch
  master
* update_golds_10_26_2021
```

Next, we decide how to take advantage of the prebuilt snapshots on the machine. Here we use the `spack manager external`
command to specify a "view" in which we want to pull external packages into our environment. Snapshots are organized by date.
With the `--latest` flag, Spack-Manager will find the latest snapshot available on your machine automatically. Here we will use the latest snapshot
and one that is attributed to our GCC with CUDA configuration, called `gcc-cuda`. Views are typically organized by compiler,
e.g. `intel`, `clang`, `gcc`, and
`gcc-cuda`, etc. We will need to "blacklist" any packages we plan on developing locally, but this happens automatically for packages
we have already set as develop specs.
```
[user@el1 user]$ spack manager external --latest -v gcc-cuda
==> Warning: included configuration files should be updated manually [files=include.yaml]
```

## Building

Once our externals and git clones are configured, we have the necessary `*.yaml` files in our `${SPACK_MANAGER}/environments/exawind` environment directory
to "concretize" and (re)install our entire project. The `spack.yaml` file in this directory is the main yaml file in which the
other yaml files are included. Concretizing is required to solve or map our loosely defined `nalu-wind@master+hypre+cuda  %gcc` spec into "concrete" parameters of our dependency graph (or DAG). The concrete DAG is _exactly_ how Spack will fulfill the dependencies for your spec. We
concretize with the command (we almost always want to use the force with `-f`). It will likely complain about us using the "original" concretizer, but this will be fixed in the future:
```
[user@el1 user]$ spack concretize -f
==> Warning: the original concretizer is currently being used.
        Upgrade to "clingo" at your earliest convenience. The original concretizer will be removed from Spack starting at v0.18.0
==> Concretized nalu-wind@master%gcc+cuda+hypre 
 -   rbzxf3n  nalu-wind@master%gcc@9.3.0~asan~boost~catalyst+cuda~fftw+hypre~ipo~openfast+pic~rocm+tests~tioga~wind-utils abs_tol=1e-15 build_type=Release cuda_arch=70 cxxstd=14 dev_path=/scratch/user/spack-manager/environments/exawind/nalu-wind rel_tol=1e-12 arch=linux-centos7-skylake_avx512
 -   b5pippu      ^cmake@3.22.1%gcc@9.3.0~doc+ncurses+openssl+ownlibs~qt build_type=Release arch=linux-centos7-skylake_avx512
 -   cwar5vn      ^cuda@11.2.2%gcc@9.3.0~allow-unsupported-compilers~dev arch=linux-centos7-skylake_avx512
 -   ukbdvpe      ^hypre@develop%gcc@9.3.0~complex+cuda~debug+fortran~gptune~int64~internal-superlu~mixedint+mpi~openmp+shared~superlu-dist+unified-memory cuda_arch=70 dev_path=/scratch/user/spack-manager/environments/exawind/hypre arch=linux-centos7-skylake_avx512
 -   ypwgjj2          ^mpt@2.22%gcc@9.3.0 arch=linux-centos7-skylake_avx512
 -   g4tc7v2          ^netlib-lapack@3.9.1%gcc@9.3.0~external-blas~ipo+lapacke+shared~xblas build_type=Release arch=linux-centos7-skylake_avx512
 -   sp3klcm      ^kokkos-nvcc-wrapper@3.2.00%gcc@9.3.0+mpi arch=linux-centos7-skylake_avx512
 -   5agjw2c      ^nccmp@1.9.0.1%gcc@9.3.0~ipo build_type=Release arch=linux-centos7-skylake_avx512
 -   p2fnhpz      ^netcdf-c@4.7.4%gcc@9.3.0~dap~fsync~hdf4~jna+mpi+parallel-netcdf+pic+shared patches=2c88dfbd6d339a0336a43b14a65a1d1df995b853b645e4af612617612a642a53 arch=linux-centos7-skylake_avx512
 -   uyq6mxb      ^trilinos@develop%gcc@9.3.0~adios2~amesos+amesos2~anasazi~aztec~basker+belos+boost~chaco~complex+cuda+cuda_rdc~debug~dtk~epetra~epetraext~epetraextbtf~epetraextexperimental~epetraextgraphreorderings+exodus+explicit_template_instantiation~float+fortran+gtest+hdf5~hypre~ifpack+ifpack2~intrepid~intrepid2~ipo~isorropia+kokkos~mesquite~minitensor~ml+mpi+muelu~mumps~nox~openmp~phalanx~piro~python~rocm~rol~rythmos~sacado~scorec+shards~shared~shylu+stk~stk_unit_tests~stokhos~stratimikos~strumpack~suite-sparse~superlu~superlu-dist~teko~tempus+tpetra~trilinoscouplings+wrapper~x11+zoltan+zoltan2 build_type=Release cuda_arch=70 cxxstd=14 dev_path=/projects/exawind/exawind-snapshots/spack-manager/environments/exawind/snapshots/eagle/2022-01-26/trilinos gotype=long patches=ffdad9a639ff490da5bd4f254e3a849b9dbf39cf7d28f8ed4419a05048846cf6 arch=linux-centos7-skylake_avx512
 -   ci73hai      ^yaml-cpp@0.6.3%gcc@9.3.0~ipo+pic+shared~tests build_type=Release arch=linux-centos7-skylake_avx512

==> Warning: included configuration files should be updated manually [files=externals.yaml, include.yaml]
```

Once our environment is concretized, we don't have to concretize again unless we change some configuration in the `*.yaml` files.
Concretization is also not explicity required for the next `spack install` command, but if any `*.yaml` files are changed, it is
recommended to `spack concretize -f`.
So now we are able to install our project with the simple command:
```
[user@el1 user]$ spack install
==> Warning: included configuration files should be updated manually [files=externals.yaml, include.yaml]
==> Installing environment /scratch/user/spack-manager/environments/exawind
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external cmake-3.22.1-b5pippuk6fzbpysv24phtw4etslotbs6)
[+] /nopt/nrel/ecom/hpacf/compilers/2020-07/spack/opt/spack/linux-centos7-skylake_avx512/gcc-8.4.0/cuda-11.2.2-5muy3vijyqputqmbdyzhltqot3fvwibu (external cuda-11.2.2-cwar5vnomowwdorf57nay6e7erladdby)
==> mpt@2.22 : has external module in ['mpt/2.22', 'slurm']
[+] /opt/hpe/hpc/mpt/mpt-2.22 (external mpt-2.22-ypwgjj2akokavha4jkpqm4prylh2vmjr)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external netlib-lapack-3.9.1-g4tc7v27alixmh2ail3lud3iweclbf52)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external kokkos-nvcc-wrapper-3.2.00-sp3klcmwurgk2hrye2tpgjv5x2pq3tlq)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external nccmp-1.9.0.1-5agjw2cs2kprcw2xm5ffmrojfc7aknnz)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external netcdf-c-4.7.4-p2fnhpzbpg7wtriqqsbudgtdwgtcrud3)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external trilinos-develop-uyq6mxbuc2lw3oext626lbmyiiyh7bqf)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external yaml-cpp-0.6.3-ci73hainzvjnag2ynsg7jxvaotnflzal)
==> Installing hypre-develop-ukbdvpe47x3frgurzhknhbfoq4iskfv3
==> No binary for hypre-develop-ukbdvpe47x3frgurzhknhbfoq4iskfv3 found: installing from source
==> No patches needed for hypre
==> hypre: Executing phase: 'autoreconf'
==> hypre: Executing phase: 'configure'
==> hypre: Executing phase: 'build'
==> hypre: Executing phase: 'install'
==> hypre: Successfully installed hypre-develop-ukbdvpe47x3frgurzhknhbfoq4iskfv3
  Fetch: 0.00s.  Build: 4m 30.38s.  Total: 4m 30.38s.
[+] /lustre/eaglefs/scratch/user/spack-manager/spack/opt/spack/linux-centos7-skylake_avx512/gcc-9.3.0/hypre-develop-ukbdvpe47x3frgurzhknhbfoq4iskfv3
==> Installing nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx
==> No binary for nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx found: installing from source
==> No patches needed for nalu-wind
==> nalu-wind: Executing phase: 'cmake'
==> nalu-wind: Executing phase: 'build'
==> nalu-wind: Executing phase: 'install'
==> nalu-wind: Successfully installed nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx
  Fetch: 0.00s.  Build: 32m 27.59s.  Total: 32m 27.59s.
[+] /lustre/eaglefs/scratch/user/spack-manager/spack/opt/spack/linux-centos7-skylake_avx512/gcc-9.3.0/nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx
```

We notice that both `nalu-wind` and `hypre` are being rebuilt, while the rest of the dependency graph is fullfilled through the externals defined from
the selected snapshot. Now that we have built and installed our first iteration of the development cycle. We can pursue editing of code
and iterate easily on a simplified build process.

## Editing Code

We start by verifying our currently activated environment in Spack:
```
[user@el1 user]$ spack find
==> In environment /scratch/user/spack-manager/environments/exawind
==> Root specs
-- no arch / gcc ------------------------------------------------
nalu-wind@master%gcc +cuda+hypre 

==> 9 installed packages
-- linux-centos7-skylake_avx512 / gcc@9.3.0 ---------------------
cuda@11.2.2  hypre@develop  mpt@2.22  nalu-wind@master  nccmp@1.9.0.1  netcdf-c@4.7.4  netlib-lapack@3.9.1  trilinos@develop  yaml-cpp@0.6.3
```

Next we will edit code in `hypre`:
```
[user@el1 user]$ cd ${SPACK_MANAGER}/environments/exawind/hypre
[user@el1 hypre]$ echo "//" >> src/HYPRE_parcsr_mgr.c
```

Then we can simply rebuild and install the entire project by:
```
[user@el1 hypre]$ spack install
==> Warning: included configuration files should be updated manually [files=externals.yaml, include.yaml]
==> Installing environment /scratch/user/spack-manager/environments/exawind
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external cmake-3.22.1-b5pippuk6fzbpysv24phtw4etslotbs6)
[+] /nopt/nrel/ecom/hpacf/compilers/2020-07/spack/opt/spack/linux-centos7-skylake_avx512/gcc-8.4.0/cuda-11.2.2-5muy3vijyqputqmbdyzhltqot3fvwibu (external cuda-11.2.2-cwar5vnomowwdorf57nay6e7erladdby)
==> mpt@2.22 : has external module in ['mpt/2.22', 'slurm']
[+] /opt/hpe/hpc/mpt/mpt-2.22 (external mpt-2.22-ypwgjj2akokavha4jkpqm4prylh2vmjr)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external netlib-lapack-3.9.1-g4tc7v27alixmh2ail3lud3iweclbf52)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external kokkos-nvcc-wrapper-3.2.00-sp3klcmwurgk2hrye2tpgjv5x2pq3tlq)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external nccmp-1.9.0.1-5agjw2cs2kprcw2xm5ffmrojfc7aknnz)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external netcdf-c-4.7.4-p2fnhpzbpg7wtriqqsbudgtdwgtcrud3)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external trilinos-develop-uyq6mxbuc2lw3oext626lbmyiiyh7bqf)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external yaml-cpp-0.6.3-ci73hainzvjnag2ynsg7jxvaotnflzal)
==> Installing hypre-develop-ukbdvpe47x3frgurzhknhbfoq4iskfv3
==> No binary for hypre-develop-ukbdvpe47x3frgurzhknhbfoq4iskfv3 found: installing from source
==> No patches needed for hypre
==> hypre: Executing phase: 'autoreconf'
==> hypre: Executing phase: 'configure'
==> hypre: Executing phase: 'clean'
==> hypre: Executing phase: 'build'
==> hypre: Executing phase: 'install'
==> hypre: Successfully installed hypre-develop-ukbdvpe47x3frgurzhknhbfoq4iskfv3
  Fetch: 0.00s.  Build: 4m 26.05s.  Total: 4m 26.05s.
[+] /lustre/eaglefs/scratch/user/spack-manager/spack/opt/spack/linux-centos7-skylake_avx512/gcc-9.3.0/hypre-develop-ukbdvpe47x3frgurzhknhbfoq4iskfv3
==> Installing nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx
==> No binary for nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx found: installing from source
==> No patches needed for nalu-wind
==> nalu-wind: Executing phase: 'cmake'
==> nalu-wind: Executing phase: 'build'
==> nalu-wind: Executing phase: 'install'
==> nalu-wind: Successfully installed nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx
  Fetch: 0.00s.  Build: 1m 33.13s.  Total: 1m 33.13s.
[+] /lustre/eaglefs/scratch/user/spack-manager/spack/opt/spack/linux-centos7-skylake_avx512/gcc-9.3.0/nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx
==> Warning: Module file /lustre/eaglefs/scratch/user/spack-manager/spack/share/spack/modules/linux-centos7-skylake_avx512/nalu-wind-master-gcc-9.3.0-rbzxf3n exists and will not be overwritten
```

Notice both `hypre` and `nalu-wind` are rebuilt. Since `nalu-wind` depends on `hypre`, it is rebuilt in order, and `nalu-wind` is relinked to `hypre`.
Spack also performed the `make install` step and the binaries are installed to regular Spack paths in `${SPACK_MANAGER}/spack/opt`. So the binaries can be referenced from the installed directory or from the build directories in each project in `${SPACK_MANAGER}/environments/exawind`.

Next we can edit code in `nalu-wind` as well, and rebuild the project:
```
[user@el1 hypre]$ cd ${SPACK_MANAGER}/environments/exawind/nalu-wind
[user@el1 nalu-wind]$ echo "//" >> unit_tests.C
[user@el1 nalu-wind]$ spack install
==> Warning: included configuration files should be updated manually [files=externals.yaml, include.yaml]
==> Installing environment /scratch/user/spack-manager/environments/exawind
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external cmake-3.22.1-b5pippuk6fzbpysv24phtw4etslotbs6)
[+] /nopt/nrel/ecom/hpacf/compilers/2020-07/spack/opt/spack/linux-centos7-skylake_avx512/gcc-8.4.0/cuda-11.2.2-5muy3vijyqputqmbdyzhltqot3fvwibu (external cuda-11.2.2-cwar5vnomowwdorf57nay6e7erladdby)
==> mpt@2.22 : has external module in ['mpt/2.22', 'slurm']
[+] /opt/hpe/hpc/mpt/mpt-2.22 (external mpt-2.22-ypwgjj2akokavha4jkpqm4prylh2vmjr)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external netlib-lapack-3.9.1-g4tc7v27alixmh2ail3lud3iweclbf52)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external kokkos-nvcc-wrapper-3.2.00-sp3klcmwurgk2hrye2tpgjv5x2pq3tlq)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external nccmp-1.9.0.1-5agjw2cs2kprcw2xm5ffmrojfc7aknnz)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external netcdf-c-4.7.4-p2fnhpzbpg7wtriqqsbudgtdwgtcrud3)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external trilinos-develop-uyq6mxbuc2lw3oext626lbmyiiyh7bqf)
[+] /projects/exawind/exawind-snapshots/spack-manager/views/exawind/snapshots/eagle/2022-01-26/gcc-cuda (external yaml-cpp-0.6.3-ci73hainzvjnag2ynsg7jxvaotnflzal)
[+] /lustre/eaglefs/scratch/user/spack-manager/spack/opt/spack/linux-centos7-skylake_avx512/gcc-9.3.0/hypre-develop-ukbdvpe47x3frgurzhknhbfoq4iskfv3
==> Installing nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx
==> No binary for nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx found: installing from source
==> No patches needed for nalu-wind
==> nalu-wind: Executing phase: 'cmake'
==> nalu-wind: Executing phase: 'build'
==> nalu-wind: Executing phase: 'install'
==> nalu-wind: Successfully installed nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx
  Fetch: 0.00s.  Build: 1m 27.78s.  Total: 1m 27.78s.
[+] /lustre/eaglefs/scratch/user/spack-manager/spack/opt/spack/linux-centos7-skylake_avx512/gcc-9.3.0/nalu-wind-master-rbzxf3nbmxodxvgvtq72n22glbd7wpdx
==> Warning: Module file /lustre/eaglefs/scratch/user/spack-manager/spack/share/spack/modules/linux-centos7-skylake_avx512/nalu-wind-master-gcc-9.3.0-rbzxf3n exists and will not be overwritten
```
Notice since nothing has changed in `hypre`, only `nalu-wind` was necessary to rebuild. We can continue to edit code and iterate simply by using the `spack install` command to rebuild the entire project concisely.

## Running

Lastly, to run the code we typically want to enter the build directory and run an executable using the environment in which it was built.
We do this by doing the following where we run the `nalu-wind` unit tests as an example. While on a compute node on the Eagle machine:
```
[user@r103u23 ~]$ spack cd -b nalu-wind
[user@r103u23 spack-build-rbzxf3n]$ spack build-env nalu-wind ./unittestX 
   Nalu-Wind Version: v1.2.0
   Nalu-Wind GIT Commit SHA: e9142052b09d6a6ddecbe9b83dedd1f7b4588fac-DIRTY
   Trilinos Version: 13.1-ga66bb9c6fa4

[==========] Running 478 tests from 116 test suites.
[----------] Global test environment set-up.
[----------] 1 test from Basic
[ RUN      ] Basic.CheckCoords1Elem
[       OK ] Basic.CheckCoords1Elem (1 ms)
[----------] 1 test from Basic (2 ms total)

[----------] 5 tests from BasicKokkos
[ RUN      ] BasicKokkos.discover_execution_space

Kokkos::Cuda is available.
Default execution space info: macro  KOKKOS_ENABLE_CUDA      : defined
macro  CUDA_VERSION          = 11020 = version 11.2
Kokkos::Cuda[ 0 ] Tesla V100-PCIE-16GB capability 7.0, Total Global Memory: 15.78 G, Shared Memory per Block: 48 K : Selected
Kokkos::Cuda[ 1 ] Tesla V100-PCIE-16GB capability 7.0, Total Global Memory: 15.78 G, Shared Memory per Block: 48 K

[       OK ] BasicKokkos.discover_execution_space (0 ms)
[ RUN      ] BasicKokkos.simple_views_1D
[       OK ] BasicKokkos.simple_views_1D (2 ms)
[ RUN      ] BasicKokkos.simple_views_2D
[       OK ] BasicKokkos.simple_views_2D (2 ms)
[ RUN      ] BasicKokkos.parallel_for
[       OK ] BasicKokkos.parallel_for (1 ms)
```

One can also obtain a bash shell with the package's build environment for performing many tasks by doing:
```
spack cd -b nalu-wind
bash -rcfile ../spack-build-env.txt
```

## Iterating

After the initial setup overhead is in place. The process for iterating in the code development can be summarized as such:
```
[user@el1 user]$ export SPACK_MANAGER=${SCRATCH}/spack-manager && source ${SPACK_MANAGER}/start.sh && spack-start && spack env activate -d ${SPACK_MANAGER}/environments/exawind
[user@el1 user]$ #edit code
[user@el1 user]$ spack install
[user@el1 user]$ spack cd -b package && spack build-env package ./exe
[user@el1 user]$ #edit code
[user@el1 user]$ spack install
[user@el1 user]$ spack cd -b package && spack build-env package ./exe
[user@el1 user]$ #edit spack.yaml
[user@el1 user]$ spack concretize -f
[user@el1 user]$ spack install
[user@el1 user]$ spack cd -b package && spack build-env package ./exe
...
```
