===============
 Spack-Manager
===============


`Spack-Manager <https://github.com/psakievich/spack-manager>`_ is a lite-weight wrapper around 
`Spack <https://github.com/spack/spack>`_ that is intended to streamline the software development and deployment cycle
for individual software projects on specific machines.

The intent of this project is to maintain as thin of a wrapper as possible around spack, and to be pushing ideas and workflow
improvements back to spack on a regular basis to reduce the code that is maintained here.
As such we do not try to fully mask spack's workflow or commands from users, but rather expose them at a level appropriate for the user type.

Spack-Manager's design is intended to serve three separate user types in a software project, and the level of expected spack exposure/knowledge required
decreases as the user becomes further removed from the build process.  The three user profiles are:

- System administrators (spack is heavily exposed and relied on)
- Code developers (some basics about spack are required, but much of the workflow can be scripted away)
- Analysts (zero exposure to spack)

Separate documentation exists for each of these user profiles.

Useful links
============
* `Developer quick start <https://psakievich.github.io/spack-manager/user_profiles/developers/developer_tutorial.html#quick-start>`_

Benefits of Spack-Manager
=========================

- Spack-Manager allows additional agility and coordination at the project level that can not be maintained for a larger tool/database such as spack. 
   This is done through heavy use of custom spack `package repositories <https://spack.readthedocs.io/en/latest/repositories.html>`_ and 
   spack's `custom extensions <https://spack.readthedocs.io/en/latest/extensions.html>`_ to allow for prototyping at the project level, as well as the option to 
   maintain features that are only intended for the project's development team.

- Spack-Manager maximizes overlap between the workflows of the three user profiles. 
   The main thought behind spack-manager is that the exact same infrastructure that the system administrators use to deploy binaries and modules on various machines
   can be recycled to run nightly tests, generate time stamped snapshots of binaries for developers to link against, and supply end users
   with production executables.
   This framework is stitched together through spack, but the end products (binaries and modules) are designed to be as independent from spack as possible.

- Spack-Manager provides the benefits of spack by seeking to maintain as small of a wrapper layer as possible. Some of these benefits include:
   - Build reproducibiilty, and scalability
   - Buy-in and feedback from HPC vendors and software developers over thousands of projects
   - Support options, extended documentation and testing through the much larger spack project

Spack-Manager is currently focused on providing the needs of the `Exawind <https://github.com/Exawind>`_ project,
but the long term intent is to make it project agnostic.  

.. toctree::
   :maxdepth: 2

   user_profiles/user_profiles
   general/general
