# Contributing Guidelines

Thank you for your interest in contributing to the project. Please adhere to to following guidelines when prepairing your contributions.

## Issues

Please feel free to make issues for any questions you have. Github issues help us stay organized and are a valuable mechanism for archiving information.
We do ask that you review our [FAQ](https://psakievich.github.io/spack-manager/general/FAQ.html) before submitting a ticket.
We try to archive the most common user issues there so it will likely save you (and us) some time.

## Pull Requests

Spack-Manager is intended to be an extension of [Spack](https://github.com/spack/spack) and so pull requests should seek to utilize Spack API's and maintain code generality.
Project and package specific changes should not propogate into any of the higher level API's in Spack-Manager.

Some notable exceptions to Spack's model that exist in our project:
- We only support python 3
- We have limited our shell support to principally bash (with a few exceptions).  We do not test or maintain posix generality.

All PR's must pass our style and testing checks and receive a review from one of the code maintainers before merging.

