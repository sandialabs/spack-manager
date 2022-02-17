# History and inspirations for Spack-Manager

Spack-Manager was created due to the challenges of building the complicated [Exawind](https://github.com/Exawind) software stack.
The Exawind codes have a relatively large number of TPL's and are designed to run on modern HPC architecture, which is currently a moving target.
These factors naturally lead toward using [Spack](https://github.com/spack/spack) to manage the build dependencies.

Arguably the most common use case for Spack is software deployment.
This was the original use for Exawind developers, and a few different extra scripts were maintained for managing the build process for Exawind software.
However, during the Exawind project Spack also released features geared toward development.
This sparked the idea for the central question behind Spack-Manager: **how much of our process can we reasonably extend into the Spack ecosystem?**

Initial evaluations of Spack's develop features were that there was potential, but also room to grow.
These features have since improved, but the other tenant of Spack-Manager was determined from this trial period:  **end products need to live as independent from Spack as possible**.
This really comes down to the fact that Exawind stack was constantly changing and growing, along with Spack itself.
In reality the entire HPC and computing landscape is changing dramatically, and so our development frameworks need to be moving together, but still have room to independently flex as thing evolve.
In this sense Spack-Manager acts as a buffer in between the larger Spack project, and the invidual software projects that are using Spack-Manager to curate their development process.

Spack-Manager's development obtained a lot of inspiration from the [Exawind-Builder](https://github.com/Exawind/exawind-builder) project.
Spack-Manager has sought to emulate some of the key features of Exawind-Builder such as the ability to use pre-configured binaries, and to allow users to quickly switch between caches.
Exawind-Builder was a tool principly designed for developers, and Spack-Manager strives to extend that user scope to the entire range of software users.

Exawind-Builder is also another example of a tool built on-top of Spack.
However, the strategies of Spack-Manager and Exawind-Builder differ slightly in that Exawind-Builder sought to go around Spack's missing features through additional bash scripting and environment configurations, while Spack-Manager seeks to predominately extend Spack using the Spack ecosystem for these scenarios.
Both sides have pro's and con's.
Choosing to go around Spack makes it easier to customize things with fewer limitations, but it also requires additional code, interfaces and maintenance.
Choosing to conform to Spack infrastructure means accepting some of the limitations and growing pains of the Spack API, but also reducing the amount of infrastructure that needs to be maintained.
This is constantly becoming less of a sacrifice due to the quality of work done by the Spack development team.

Spack-Manager is intended to be agile, and adapt to changes in Spack by embracing new features in Spack, and contributing back everything it can to the Spack project.
In this sense we are able to harness the pro's of Spack, while still customizing our workflow and influencing the growth of Spack in the future.



  