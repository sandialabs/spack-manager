import os
import pytest


def test_can_read_exawind_repo(create_package):
    package = create_package('nalu-wind-nightly')
    #package.ctest_args()  # test chokes on setting CMAKE_CXX_COMPILER from mpi spec ...
    assert package.spec.variants['extra_name'].value == 'default'
