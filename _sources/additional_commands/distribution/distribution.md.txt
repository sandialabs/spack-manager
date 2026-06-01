# Distribution Command

The distribution command bundles an active Spack environment into a self-contained hierarchy.  When run, the command selects the necessary components of a Spack environment to retain so that the resultant bundle can be re-installed on another machine without the need to acquire any outside resources.  An exact copy of the exact version of Spack used to create the distribution bundle, as a bootstrap mirror, any installed Spack extensions, all package repositories, and a source mirror are included alongside a configured Spack environment. The resultant hierarchy looks like this:
```
.
|- distro
    |- bootstrap-mirror
    |- environment
    |- extensions
    |- spack
    |- spack_repo
```

## Modifying the generated Spack envrionment
The `distribution` command includes optional behavior that allows the user to modify the generated Spack environment by including/excluding sections from the `spack.yaml` that is being sourced from the active environment. This is achieved by passing a directory containing relevant Spack YAML files to either include or exclude. For example `/path/to/excludes/packages.yaml` would be provided via `--exclude /path/to/excludes` and might look like this:

```yaml
packages: 
    cxx: {}
    all:
        providers:
            lapack: [netlib-lapack]
```
The above YAML would prevent `cxx` from appearing in the list of packages entirely and would prevent `netlib-lapack` from appearing in the list of valid `lapack` providers.

Similarly, directories passed with `--include` would be copied into the distribution and added to its environment in the `include` section.

## Using the resultant pacakge
To install the package that was created by `spack manager distribution` an end user needs to source the included `setup-env.*` script from the included copy of Spack, activate the included environment, configure a desired compiler, and install.  For example:
```bash
. distro/spack/share/spack/setup-env.sh
spack env activate distro/environment
spack compiler find
spack install
```