# Externals and snapshots

One of the prominent and unique features of Spack-Manager is the ability for developers to automatically link against binaries
that were created in a snapshot of builds, or even between individual developer environments.
This feature is enabled through Spack's external specification for packages, and is automated with the `spack manager external` command.

Spack has several ways of reusing previous builds, and sharing binaries.
The major ways of doing this are:

- Re-using packages in the current Spack database: Standard operation and through the `--reuse` flag
- Buildcaches: Indpepndent binary caches that can be hosted on webservers and filesystems
- Upstreams: Chaining Spack installations so that the installed packages in the upstream versions are usable and read-only downstream
- Externals: Manually specifying the path or module for a known installation of software

All of these options were evaluated during the inception of Spack-Manager, but the first three were discarded for the same fundamental reason:
the control over which software you get is not stricitly yours.
For all three cases you must rely on the concretizer to pick a compatible software installation for you.
Externals are the only way to take explicit control and force Spack to use libraries from a specific location of your choosing.

## How is an external defined

## CMD: `spack manager external`

## How to use `spack manager external` to share binares with others

## Relationship with Spack-Manager snapshots