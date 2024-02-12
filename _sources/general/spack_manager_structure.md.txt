# Spack-Manager Structure

Spack-Manager is a Spack extension that provides a way for software applications
to configure their usage of spack.  
The code of Spack-Manager is independent of each individual application and each
application code needs to configure a Spack-Manager `Project` to tell Spack-Manager how to work
with their application.

A `Project` at its core is simply a collection of [spack configuration files](https://spack.readthedocs.io/en/latest/configuration.html),
and [spack package repositories](https://spack.readthedocs.io/en/latest/repositories.html).
A few other optional hooks will be discussed below.

The configuration files in a `Project` are organized based on the configuration bifurcations that the projects supports.
These are called `Machines` based on the guiding principle that spack configurations typically have to be
changed when the machine/system is changed.

`Projects` can be registered with Spack-Manager by adding them to the `spack-manager.yaml` configuration file.
This file lives in the Spack-Manager directory and controls settings for `Spack-Manager` and the `Projects` that
are registered.

``` yaml
spack-manager:
  projects:
    - /path/to/project_a
      default_view: False
    - $HOME/project_b
```

Additional data about this file can be found at *TBD*.
Information on configuring a new `Project` can be found in the system administrator profile documentation (add link).
