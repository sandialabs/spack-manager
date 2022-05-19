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
        '''nalu-wind-nightly +fftw+tioga+hypre+openfast+cuda cuda_arch=70 %gcc@9.3.0
        ^cuda@11.2.2 ^trilinos@develop+uvm''')
    assert (package.dashboard_build_name() ==
            '-gcc@9.3.0-cuda@11.2.2^trilinos@develop+uvm')
    package = create_package(
        'nalu-wind-nightly +fftw+tioga+hypre+openfast %gcc@9.3.0 ^trilinos@develop')
    assert package.dashboard_build_name() == '-gcc@9.3.0^trilinos@develop'
    package = create_package(
        'nalu-wind-nightly +fftw+tioga+hypre+openfast %intel@20.0.2 ^trilinos@develop')
    assert package.dashboard_build_name() == '-intel@20.0.2^trilinos@develop'
    package = create_package(
        '''nalu-wind-nightly +fftw+tioga+hypre+openfast+asan build_type=Debug
        %clang@10.0.0 ^trilinos@develop''')
    assert package.dashboard_build_name() == '-clang@10.0.0^trilinos@develop'


def test_snl_build_names(create_package):
    package = create_package(
        '''nalu-wind-nightly+snl +fftw+tioga+hypre+openfast %gcc@9.3.0
        build_type=Release ^trilinos@develop''')
    assert (package.dashboard_build_name() ==
            '-gcc@9.3.0-Release+fftw+tioga+hypre+openfast^trilinos@develop')
    package = create_package(
        'nalu-wind-nightly+snl %gcc@9.3.0 build_type=Release ^trilinos@develop')
    assert package.dashboard_build_name() == '-gcc@9.3.0-Release^trilinos@develop'
    package = create_package(
        'nalu-wind-nightly+snl %gcc@9.3.0 build_type=Debug ^trilinos@develop')
    assert package.dashboard_build_name() == '-gcc@9.3.0-Debug^trilinos@develop'
    package = create_package(
        '''nalu-wind-nightly+snl +fftw+tioga+hypre+openfast+cuda cuda_arch=70 %gcc@9.3.0
        build_type=Release ^cuda@11.2.2 ^trilinos@develop+uvm''')
    assert (package.dashboard_build_name() ==
            '-gcc@9.3.0-cuda@11.2.2-Release+fftw+tioga+hypre+openfast'
            '^trilinos@develop+uvm')
    package = create_package(
        '''nalu-wind-nightly+snl +cuda cuda_arch=70 %gcc@9.3.0
        build_type=Release ^cuda@11.2.2 ^trilinos@develop+uvm''')
    assert (package.dashboard_build_name() ==
            '-gcc@9.3.0-cuda@11.2.2-Release^trilinos@develop+uvm')
    package = create_package(
        '''nalu-wind-nightly+snl +cuda cuda_arch=70 %gcc@9.3.0
        build_type=Debug ^cuda@11.2.2 ^trilinos@develop+uvm''')
    assert (package.dashboard_build_name() ==
            '-gcc@9.3.0-cuda@11.2.2-Debug^trilinos@develop+uvm')
    package = create_package(
        '''nalu-wind-nightly+snl +fftw+tioga+hypre+openfast+cuda cuda_arch=70 %gcc@9.3.0
        build_type=Release ^cuda@11.2.2 ^trilinos@develop~uvm''')
    assert (package.dashboard_build_name() ==
            '-gcc@9.3.0-cuda@11.2.2-Release+fftw+tioga+hypre+openfast'
            '^trilinos@develop~uvm')
    package = create_package(
        '''nalu-wind-nightly+snl +cuda cuda_arch=70 %gcc@9.3.0
        build_type=Release ^cuda@11.2.2 ^trilinos@develop~uvm''')
    assert (package.dashboard_build_name() ==
            '-gcc@9.3.0-cuda@11.2.2-Release^trilinos@develop~uvm')
    package = create_package(
        '''nalu-wind-nightly+snl +cuda cuda_arch=70 %gcc@9.3.0
        build_type=Debug ^cuda@11.2.2 ^trilinos@develop~uvm''')
    assert (package.dashboard_build_name() ==
            '-gcc@9.3.0-cuda@11.2.2-Debug^trilinos@develop~uvm')


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


def test_dashboard_variants_build_type_release(create_package):
    package = create_package('nalu-wind-nightly build_type=Release')
    assert package.dashboard_variants() == 'Release'


def test_dashboard_variants_build_type_debug(create_package):
    package = create_package('nalu-wind-nightly build_type=Debug')
    assert package.dashboard_variants() == 'Debug'


def test_dashboard_variants_contains_enabled(create_package):
    package = create_package('nalu-wind-nightly+hypre build_type=Release')
    assert package.dashboard_variants() == 'Release+hypre'


def test_dashboard_variants_contains_multiple_enabled(create_package):
    package = create_package(
        'nalu-wind-nightly+fftw+hypre+tioga+openfast build_type=Release')
    assert package.dashboard_variants() == 'Release+fftw+hypre+tioga+openfast'


def test_dashboard_variants_doesnt_contain_non_whitelisted(create_package):
    package = create_package(
        '''nalu-wind-nightly+fftw+hypre+tioga+openfast+snl+cuda
        cuda_arch=70 abs_tol=1e-15 build_type=Release''')
    assert package.dashboard_variants() == 'Release+fftw+hypre+tioga+openfast'


def test_dashboard_variants_doesnt_contain_disabled(create_package):
    package = create_package(
        'nalu-wind-nightly+fftw~hypre+tioga~openfast build_type=Release')
    assert package.dashboard_variants() == 'Release+fftw+tioga'
