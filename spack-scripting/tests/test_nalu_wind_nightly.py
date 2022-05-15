import os
import pytest


def test_package_name(packages):
    package = packages.create('nalu-wind-nightly')
    assert package.name == 'nalu-wind-nightly'

def test_package_picks_up_variants(packages):
    package = packages.create('nalu-wind-nightly+snl')
    assert package.spec.variants['snl'].value

def test_package_picks_up_default_variants(packages):
    package = packages.create('nalu-wind-nightly')
    assert not package.spec.variants['snl'].value
