# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.


def test_package_name(create_package):
    package = create_package('nalu-wind-nightly')
    assert package.name == 'nalu-wind-nightly'


def test_nrel_build_names(create_package):
    package = create_package(
            'nalu-wind-nightly +fftw+tioga+hypre+openfast+cuda cuda_arch=70 %gcc@9.3.0 ^cuda@11.2.2 ^trilinos@develop+uvm')
    assert package.dashboard_build_name() == '-gcc@9.3.0-cuda@11.2.2^trilinos@develop+uvm'
    package = create_package('nalu-wind-nightly +fftw+tioga+hypre+openfast %gcc@9.3.0 ^trilinos@develop')
    assert package.dashboard_build_name() == '-gcc@9.3.0^trilinos@develop'
    package = create_package('nalu-wind-nightly +fftw+tioga+hypre+openfast %intel@20.0.2 ^trilinos@develop')
    assert package.dashboard_build_name() == '-intel@20.0.2^trilinos@develop'
    package = create_package('nalu-wind-nightly +fftw+tioga+hypre+openfast+asan build_type=Debug %clang@10.0.0 ^trilinos@develop')
    assert package.dashboard_build_name() == '-clang@10.0.0^trilinos@develop'


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


def test_dashboard_trilinos_develop(create_package):
    package = create_package('nalu-wind-nightly ^trilinos@develop')
    assert package.dashboard_trilinos() == 'trilinos@develop'


def test_dashboard_trilinos_master(create_package):
    package = create_package('nalu-wind-nightly ^trilinos@master')
    assert package.dashboard_trilinos() == 'trilinos@master'


def test_dashboard_trilinos_no_cuda_no_uvm_option(create_package):
    package = create_package('nalu-wind-nightly ^trilinos@develop~uvm')
    assert package.dashboard_trilinos() == 'trilinos@develop'


def test_dashboard_trilinos_cuda_uvm(create_package):
    package = create_package('nalu-wind-nightly ^cuda@11.2.2 ^trilinos@develop+uvm')
    assert package.dashboard_trilinos() == 'trilinos@develop+uvm'


def test_dashboard_trilinos_cuda_no_uvm(create_package):
    package = create_package('nalu-wind-nightly ^cuda@10.1.243 ^trilinos@develop~uvm')
    assert package.dashboard_trilinos() == 'trilinos@develop~uvm'
