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


def create_spack_manifest(path, specs=None, extra_data=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not specs:
        specs = []
    data =  {
            "specs": specs
    }
    if extra_data:
        data.update(extra_data)
    data = {"spack": data}
    
    with open(path, "w") as outf:
        spack.util.spack_yaml.dump(
            data, outf, default_flow_style=False
        )
    return data


def create_pacakge_manifest(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {
        "packages": {
            "all": {
                "providers": {
                    "mpi": ["openmpi"]
                }
            }
        }
    }
    with open(path, "w") as outf:
        spack.util.spack_yaml.dump(
            data, outf, default_flow_style=False
        )
    return data


def create_extension(extension_name):
    base_name = os.path.basename(extension_name).split("spack-")[-1]
    extension_file = os.path.join(extension_name, base_name, "cmd", f"{base_name}.py")
    content = f"""\
def {base_name}(parser, args):
    return None
"""
    os.makedirs(os.path.dirname(extension_file))
    with open(extension_file, "w") as f:
        f.write(content)


def create_repo(path):
    os.makedirs(path)
    data = {
        "repo": {
            "namespace": "test"
        }
    }
    with open(os.path.join(path, "repo.yaml"), "w") as f:
        spack.util.spack_yaml.dump(
            data, f, default_flow_style=False
        )
    package = os.path.join(path, "packages", "test")
    os.makedirs(package)
    package_content = """\
from spack.package import *

class Test(Package):
    pass
"""
    with open(os.path.join(package, "package.py"), "w") as f:
        f.write(package_content)


def get_manifest(env):
    manifest = os.path.join(env.path, "spack.yaml")
    with open(manifest) as f:
        return spack.util.spack_yaml.load(f)


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


def test_remove_subset_from_dict():
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
    data = create_spack_manifest(manifest)

    env = spack.environment.environment_from_name_or_dir(os.path.dirname(manifest))
    assert distribution.get_env_as_dict(env) == data


def test_get_local_config(tmpdir):
    packages = os.path.join(tmpdir.strpath, "dir", "packages.yaml")
    data = create_pacakge_manifest(packages)

    result = distribution.get_local_config("local", os.path.dirname(packages))
    assert result == data


def test_get_valid_env_scopes(tmpdir):
    manifest = os.path.join(tmpdir.strpath, "env", "spack.yaml")
    packages = os.path.join(tmpdir.strpath, "dir", "packages.yaml")

    extra_data = {
        "include": [
            os.path.dirname(packages)
        ],
    }
    create_spack_manifest(manifest, extra_data=extra_data)
    create_pacakge_manifest(packages)

    env = spack.environment.environment_from_name_or_dir(os.path.dirname(manifest))
    with env:
        scope_names = distribution.valid_env_scopes(env)
    assert len(scope_names) == 2


def test_DistributionPackager_wipe_n_make(tmpdir):
    root = os.path.join(tmpdir.strpath, "root")

    pkgr = distribution.DistributionPackager(None, root)
    assert not os.path.isdir(root)
    pkgr.wipe_n_make()
    assert os.path.isdir(root)
    test_file = os.path.join(root, "test")
    with open(test_file, "w") as outf:
        outf.write("content")
    assert os.path.isfile(test_file)
    pkgr.wipe_n_make()
    assert not os.path.isfile(test_file)


def get_fake_concretize_env(path):
    class MockEnv(spack.environment.Environment):
        def concretize(self, *args, **kwargs):
            os.makedirs(os.path.join(self.path, ".spack-env"), exist_ok=True)
            with open(os.path.join(self.path, "spack.lock"), "w") as f:
                f.write("content")

        def write(self, *args, **kwargs):
            pass

    return MockEnv(path)


def test_DistributionPackager_finalize(tmpdir):
    root = os.path.join(tmpdir.strpath, "root")
    manifest = os.path.join(root, "environment", "spack.yaml")
    extra_data = {
        "packages": {
            "gcc" : {
                "require": ["@1.2.3"]
            }
        }
    }
    create_spack_manifest(manifest, extra_data=extra_data)
    env_dir = os.path.dirname(manifest)
    env = get_fake_concretize_env(env_dir)

    pkgr = distribution.DistributionPackager(None, root)
    pkgr._env = env
    pkgr.finalize()
    
    lockfile = os.path.join(env_dir, "spack.lock")
    content = get_manifest(pkgr.env)

    assert os.path.isfile(lockfile)
    assert "packages" in content["spack"]
    assert "specs" in content["spack"]


def test_DistributionPackager_finalize_with_excludes(tmpdir):
    root = os.path.join(tmpdir.strpath, "root")
    exclude_dir = os.path.join(tmpdir.strpath, "excludes")
    exclude_file = os.path.join(exclude_dir, "packages.yaml")
    os.makedirs(exclude_dir)
    data = {
        "packages": {
            "gcc": {}
        }
    }
    with open(exclude_file, "w") as outf:
        spack.util.spack_yaml.dump(
            data, outf, default_flow_style=False
        )
    manifest = os.path.join(root, "environment", "spack.yaml")
    extra_data = {
        "packages": {
            "gcc" : {
                "require": ["@1.2.3"]
            }
        }
    }
    create_spack_manifest(manifest, extra_data=extra_data)
    env_dir = os.path.dirname(manifest)
    env = get_fake_concretize_env(env_dir)

    pkgr = distribution.DistributionPackager(None, root, excludes=exclude_dir)
    pkgr._env = env
    pkgr.finalize()
    
    lockfile = os.path.join(env_dir, "spack.lock")
    content = get_manifest(pkgr.env)

    assert os.path.isfile(lockfile)
    assert "packages" not in content["spack"]
    assert "specs" in content["spack"]


def test_DistributionPackager_clean(tmpdir):
    root = os.path.join(tmpdir.strpath, "root")
    manifest = os.path.join(root, "environment", "spack.yaml")
    create_spack_manifest(manifest)
    env_dir = os.path.dirname(manifest)
    env = get_fake_concretize_env(env_dir)

    pkgr = distribution.DistributionPackager(None, root)
    pkgr._env = env
    
    pkgr.finalize()
    assert len(os.listdir(env_dir)) == 3
    pkgr.clean()
    env_assets =  os.listdir(env_dir)
    assert len(env_assets) == 1
    assert "spack.yaml" in env_assets


def test_DistributionPackager_configure_includes(tmpdir):
    root = os.path.join(tmpdir.strpath, "root")
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest)
    env = spack.environment.Environment(os.path.dirname(manifest))

    includes_dir = os.path.join(tmpdir.strpath, "includes")
    includes = os.path.join(includes_dir, "packages.yaml")
    create_pacakge_manifest(includes)
    pkgr = distribution.DistributionPackager(env, root, includes=includes_dir)

    content = get_manifest(pkgr.env)
    copied_includes = os.path.join(root, "includes", "packages.yaml")
    assert "include" not in content["spack"]
    assert not os.path.isfile(copied_includes)

    pkgr.configure_includes()
    new_content = get_manifest(pkgr.env)

    assert "include" in new_content["spack"]
    assert os.path.isfile(copied_includes)


def test_DistributionPackager_configure_specs(tmpdir):
    root = os.path.join(tmpdir.strpath, "root")
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    specs = ["zlib"]
    create_spack_manifest(manifest, specs=specs)
    env = spack.environment.Environment(os.path.dirname(manifest))

    pkgr = distribution.DistributionPackager(env, root)

    assert pkgr.env.user_specs.specs_as_yaml_list == []
    pkgr.configure_specs()
    assert pkgr.env.user_specs.specs_as_yaml_list == specs
    
    
def test_DistributionPackager_configure_extensions(tmpdir):
    root = os.path.join(tmpdir.strpath, "root")
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    extensions = [
        os.path.join(tmpdir.strpath, "extensions", "spack-extensiona"),
        os.path.join(tmpdir.strpath, "extensions", "spack-extensionb")

    ]
    expected_extensions = [os.path.join('..', "extensions", "spack-manager")]
    for ext in extensions:
        expected_extensions.append(os.path.join('..', "extensions", os.path.basename(ext)))
        create_extension(ext)

    extra_data = {
        "config": {
            "extensions": extensions
        }
    }
    create_spack_manifest(manifest, extra_data=extra_data)
    env = spack.environment.Environment(os.path.dirname(manifest))

    pkgr = distribution.DistributionPackager(env, root)
    content = get_manifest(pkgr.env)
    assert "extensions" not in content["spack"].get("config", {})
    for extension in expected_extensions:
        assert not os.path.isdir(extension)

    pkgr.configure_extensions()
    mod_content = get_manifest(pkgr.env)
    print("content", mod_content)

    for extension in expected_extensions:
        assert os.path.isdir(os.path.join(pkgr.env.path, extension))
    assert "extensions" in mod_content["spack"].get("config", {})
    assert set(mod_content["spack"]["config"]["extensions"]) == set(expected_extensions)


def test_DistributionPackager_configure_repos(tmpdir):
    package_repo = os.path.join(tmpdir.strpath, "mock-repo")
    create_repo(package_repo)
    
    extra_data = {
        "repos": [
            package_repo
        ]
    }
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest, extra_data=extra_data)
    env = spack.environment.Environment(os.path.dirname(manifest))

    root = os.path.join(tmpdir.strpath, "root")
    pkgr = distribution.DistributionPackager(env, root)

    expected_repo = os.path.join(pkgr.package_repos, os.path.basename(package_repo))
    initial_config = get_manifest(pkgr.env)
    assert not os.path.isdir(expected_repo)
    assert "repos" not in initial_config["spack"]
    pkgr.configure_package_repos()
    result_config = get_manifest(pkgr.env)
    assert os.path.isdir(expected_repo)
    assert "repos" in result_config["spack"]
    assert os.path.relpath(expected_repo, pkgr.env.path) in result_config["spack"]["repos"]


def test_DistributionPackager_configure_package_settings(tmpdir): 
    good = {
        "all": {
                "prefer": ["generator=Ninja"]
        }
    }
    bad = {
        "cmake": {
                "externals": [
                    {
                        "spec": "cmake@1.2.3",
                        "path": "/foo/bar"
                    }
                ]
        }
    }
    
    extra_data = {
        "packages": {}
    }
    extra_data["packages"].update(good)
    extra_data["packages"].update(bad)
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest, extra_data=extra_data)
    env = spack.environment.Environment(os.path.dirname(manifest))
    root = os.path.join(tmpdir.strpath, "root")

    pkgr = distribution.DistributionPackager(env, root)

    inital_config = get_manifest(pkgr.env)
    assert "packages" not in inital_config["spack"]
    pkgr.configure_package_settings()
    result_config = get_manifest(pkgr.env)
    assert "packages" in result_config["spack"]
    assert good == result_config["spack"]["packages"]


def test_DistributionPackager_bundle_extra_data(tmpdir):
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest)
    env = spack.environment.Environment(os.path.dirname(manifest))
    
    extra_data = os.path.join(tmpdir.strpath, "data")
    os.makedirs(extra_data)
    extra_file_a = os.path.join(extra_data, "file_a.txt")
    extra_file_b = os.path.join(extra_data, "sub_dir", "file_b.txt")
    os.makedirs(os.path.dirname(extra_file_b))
    with open(extra_file_b, "w") as f:
        f.write("content")
    with open(extra_file_a, "w") as f:
        f.write("content")

    root = os.path.join(tmpdir.strpath, "root")
    expect_file_a = extra_file_a.replace(extra_data, root)
    expect_file_b = extra_file_b.replace(extra_data, root)

    pkgr = distribution.DistributionPackager(env, root, extra_data=extra_data)
    pkgr.bundle_extra_data()
    assert os.path.isfile(expect_file_a)
    assert os.path.isfile(expect_file_b)


def test_DistributionPackager_context_erases_working_dir(tmpdir):
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest)
    env = spack.environment.Environment(os.path.dirname(manifest))
    root = os.path.join(tmpdir.strpath, "root")
    pkgr = distribution.DistributionPackager(env, root)

    testfile = os.path.join(root, "testfile")
    os.makedirs(root)
    with open(testfile, "w") as f:
        f.write("content")
    with env:
        assert spack.environment.active_environment().name == env.name
        with pkgr:
            assert spack.environment.active_environment() is None
            assert not os.path.exists(testfile)
        assert spack.environment.active_environment().name == env.name


def test_DistributionPackager_context_creates_working_dir(tmpdir):
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest)
    env = spack.environment.Environment(os.path.dirname(manifest))
    root = os.path.join(tmpdir.strpath, "root")
    pkgr = distribution.DistributionPackager(env, root)

    with env:
        assert spack.environment.active_environment().name == env.name
        with pkgr:
            assert spack.environment.active_environment() is None
            assert os.path.isdir(root)
        assert spack.environment.active_environment().name == env.name