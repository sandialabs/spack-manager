# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.


def test_package_name(create_package):
    package = create_package('nalu-wind-nightly')
    assert package.name == 'nalu-wind-nightly'


def test_dashboard_compilers_gcc_compiler(create_package):
    package = create_package('nalu-wind-nightly%gcc@9.3.0')
    assert package.dashboard_compilers() == 'gcc@9.3.0'


def test_dashboard_compilers_intel_compiler(create_package):
    package = create_package('nalu-wind-nightly%intel@20.0.2')
    assert package.dashboard_compilers() == 'intel@20.0.2'


def test_dashboard_compilers_gcc_compiler_with_cuda(create_package):
    package = create_package('nalu-wind-nightly%gcc@9.3.0^cuda@11.2.2')
    assert package.dashboard_compilers() == 'gcc@9.3.0-cuda@11.2.2'


def test_dashboard_compilers_cuda_version_pulled_from_spec(create_package):
    package = create_package('nalu-wind-nightly%gcc@9.3.0^cuda@11.4.2')
    assert package.dashboard_compilers() == 'gcc@9.3.0-cuda@11.4.2'
