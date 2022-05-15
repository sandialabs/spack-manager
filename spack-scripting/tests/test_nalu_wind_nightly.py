# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.


def test_package_name(create_package):
    package = create_package('nalu-wind-nightly')
    assert package.name == 'nalu-wind-nightly'


def test_package_picks_up_variants(create_package):
    package = create_package('nalu-wind-nightly+snl')
    assert package.spec.variants['snl'].value


def test_package_picks_up_default_variants(create_package):
    package = create_package('nalu-wind-nightly')
    assert 'snl' not in package.spec.variants
