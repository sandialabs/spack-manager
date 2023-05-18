# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from manager_cmds.pin import pin_graph

from spack.spec import Spec
from spack.version import GitVersion


# =============================================================================
# These tests  are really slow because we have to concretize
# it would be good to come up with a quick concretization test suite
# or figure out how to mock it, we may want to consider disabling at some point
# =============================================================================
def test_version_replacement_preserves_all_but_version():
    spec_str = "nalu-wind@master+hypre%gcc build_type=Release"
    spec = Spec(spec_str)
    spec.concretize()
    new_spec_str = pin_graph(spec)
    assert "nalu-wind" in new_spec_str
    assert "git." in new_spec_str
    assert "=master" in new_spec_str
    assert "+hypre" in new_spec_str
    assert "%gcc" in new_spec_str
    assert " build_type=Release" in new_spec_str


def test_version_replacement_string_creates_spec_with_git_ref_version():
    spec_str = "nalu-wind@master+hypre%gcc build_type=Release"
    spec = Spec(spec_str)
    spec.concretize()
    new_spec_str = pin_graph(spec)
    new_spec = Spec(new_spec_str)
    assert isinstance(new_spec.version, GitVersion)


# =============================================================================
