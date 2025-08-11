# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import spack
import spack.main
import spack.extensions.manager.manager_cmds.distribution as distribution

manager = spack.main.SpackCommand("manager")


def test_is_match():
    patterns = ["*.yaml", "*.yml", "yaml/*"]
    assert distribution.is_match("file.yaml", patterns)
    assert distribution.is_match("file.yml", patterns)
    assert distribution.is_match("yaml/file.txt", patterns)
    assert not distribution.is_match("file.txt", patterns)
    assert not distribution.is_match("/foo/yaml/file.py", patterns)

def test_copy_files_excluding_pattern(tmpdir):
    root = os.path.join(tmpdir.strpath, "foo")
    paths = [
        os.path.join(root, "bar", "file.txt"),
        os.path.join(root, "bar", "other.txt"),
        os.path.join(root, "baz", "file.txt"),
        os.path.join(root, "bing", "bang", "other.txt"),
        os.path.join(root, "bing", "file.txt"),
    ]
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write("content")

    dest = os.path.join(tmpdir.strpath, "dest")
    ignore = ["bar/other.txt", "bing/bang/*"]
    distribution.copy_files_excluding_pattern(root, dest, ignore)

    results = []
    for _, _, files in os.walk(dest):
        assert "other.txt" not in files
        results.extend(files)
    assert len(results) == 3

def test_remove_subset_from_dict_invalid_subset():
    data = {
        "a": 1,
    }
    orig = data.copy()
    subset = {
        "b": None,
    }
    distribution.remove_subset_from_dict(data, subset)
    assert data == orig

def test_remove_subset_from_dict_invalid_subset():
    data = {
        "a": 1,
        "b": {
            "c": 2,
            "d": 3,
        },
        "e": [1, 2, 3],
        "f": [1, 2]
    }
    orig = data.copy()
    subset = {
        "a": None,
        "b": {
            "c": None
        },
        "e": [1],
        "f": [1, 2]
    }
    expected = {
        "b": {
            "d": 3,
        },
        "e": [2, 3]
    }
    distribution.remove_subset_from_dict(data, subset)
    assert data != orig
    assert data == expected

def test_get_env_as_dict(tmpdir):
    manifest = os.path.join(tmpdir.strpath, "env", "spack.yaml")
    os.makedirs(os.path.dirname(manifest))
    data = {
        "spack": {
            "specs": [
                "zlib"
            ]
        }
    }
    with open(manifest, "w") as outf:
        spack.util.spack_yaml.dump(
            data, outf, default_flow_style=False
        )
    env = spack.environment.environment_from_name_or_dir(os.path.dirname(manifest))
    assert distribution.get_env_as_dict(env) == data

def test_get_local_config(tmpdir):
    packages = os.path.join(tmpdir.strpath, "dir", "packages.yaml")
    os.makedirs(os.path.dirname(packages))
    data = {
        "packages": {
            "all": {
                "providers": {
                    "mpi": ["openmpi"]
                }
            }
        }
    }
    with open(packages, "w") as outf:
        spack.util.spack_yaml.dump(
            data, outf, default_flow_style=False
        )
    result = distribution.get_local_config("local", os.path.dirname(packages))

    assert result == data

def test_get_valid_env_scopes(tmpdir):
    manifest = os.path.join(tmpdir.strpath, "env", "spack.yaml")
    packages = os.path.join(tmpdir.strpath, "dir", "packages.yaml")
    os.makedirs(os.path.dirname(packages))
    data = {
        "packages": {
            "all": {
                "providers": {
                    "mpi": ["openmpi"]
                }
            }
        }
    }
    with open(packages, "w") as outf:
        spack.util.spack_yaml.dump(
            data, outf, default_flow_style=False
        )

   
    os.makedirs(os.path.dirname(manifest))
    data = {
        "spack": {
            "include": [
                os.path.dirname(packages)
            ],
            "specs": [
                "zlib"
            ]
        }
    }
    with open(manifest, "w") as outf:
        spack.util.spack_yaml.dump(
            data, outf, default_flow_style=False
        )
    env = spack.environment.environment_from_name_or_dir(os.path.dirname(manifest))
    with env:
        scope_names = distribution.valid_env_scopes(env)
        assert len(scope_names) == 2