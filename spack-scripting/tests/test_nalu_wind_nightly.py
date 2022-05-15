import os
import pytest


def test_package_name(create_package):
    package = create_package('nalu-wind-nightly')
    assert package.name == 'nalu-wind-nightly'

def test_package_picks_up_variants(create_package):
    package = create_package('nalu-wind-nightly+snl')
    assert package.spec.variants['snl'].value

def test_package_picks_up_default_variants(create_package):
    package = create_package('nalu-wind-nightly')
    assert 'snl' not in package.spec.variants
