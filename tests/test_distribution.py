# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import inspect
import os
from argparse import ArgumentParser

import pytest

import spack
import spack.cmd.bootstrap as test_bootstrap_parse
import spack.cmd.buildcache as test_buildcache_parse
import spack.cmd.mirror as test_mirror_parse
import spack.environment
import spack.extensions.manager.manager_cmds.distribution as distribution
import spack.util.spack_yaml
import spack.verify


def create_spack_manifest(path, specs=None, extra_data=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not specs:
        specs = []
    data = {"specs": specs}
    if extra_data:
        data.update(extra_data)
    data = {"spack": data}

    with open(path, "w") as outf:
        spack.util.spack_yaml.dump(data, outf, default_flow_style=False)
    return data


def create_pacakge_manifest(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {"packages": {"all": {"providers": {"mpi": ["openmpi"]}}}}
    with open(path, "w") as outf:
        spack.util.spack_yaml.dump(data, outf, default_flow_style=False)
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
    data = {"repo": {"namespace": "test"}}
    with open(os.path.join(path, "repo.yaml"), "w") as f:
        spack.util.spack_yaml.dump(data, f, default_flow_style=False)
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
    """
    This test verifies that the `is_match` function correctly identifies whether a given file
    path matches any of the specified glob patterns. The patterns used in this test file
    extensions and a directory pattern.
    """
    patterns = ["*.yaml", "*.yml", "yaml/*"]
    assert distribution.is_match("file.yaml", patterns)
    assert distribution.is_match("file.yml", patterns)
    assert distribution.is_match("yaml/file.txt", patterns)
    assert not distribution.is_match("file.txt", patterns)
    assert not distribution.is_match("/foo/yaml/file.py", patterns)


def test_copy_files_excluding_pattern(tmpdir):
    """
    Test the recursive copying of files from a source directory to a destination directory,
    excluding files and directories that match specified patterns.

    This test creates a temporary directory structure with several files, and multiple levels
    then invokes the `copy_files_excluding_pattern` function to copy files from the source
    directory to the destination directory while ignoring files and directories that match the
    provided exclusion patterns.
    """
    root = os.path.join(tmpdir.strpath, "foo")
    paths = [
        os.path.join(root, "bar", "file.txt"),
        os.path.join(root, "bar", "bad.txt"),
        os.path.join(root, "baz", "file.txt"),
        os.path.join(root, "bing", "bang", "bad.txt"),
        os.path.join(root, "bing", "file.txt"),
    ]
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write("content")

    dest = os.path.join(tmpdir.strpath, "dest")
    ignore = ["bar/bad.txt", "bing/bang/*"]
    distribution.copy_files_excluding_pattern(root, dest, ignore)

    results = []
    for _, _, files in os.walk(dest):
        assert "bad.txt" not in files
        results.extend(files)
    assert len(results) == 3


def test_remove_subset_from_dict():
    """
    This test verifies that the `remove_subset_from_dict` function correctly removes specified keys
    and their associated values from a dictionary, including nested dictionaries and lists.

    Keys should be recursively removed from the dictionary when their values become empty. In
    instances where the value of the subset dictionary is a list, remove the entry in the list
    from the primary dictionary if it exists.
    """
    data = {"a": 1, "b": {"c": 2, "d": 3}, "e": [1, 2, 3], "f": [1, 2]}
    subset = {"a": None, "b": {"c": None}, "e": [1], "f": [1, 2]}
    expected = {"b": {"d": 3}, "e": [2, 3]}
    distribution.remove_subset_from_dict(data, subset)
    assert data == expected


def test_remove_subset_from_dict_invalid_subset():
    """
    This test verifies that the `remove_subset_from_dict` function does not modify the primary
    dictionary if the subset dictionary is not a valid subset of the primary dictionary.
    """
    data = {"a": 1}
    orig = data.copy()
    subset = {"b": None}
    distribution.remove_subset_from_dict(data, subset)
    assert data == orig


def test_get_env_as_dict(tmpdir):
    """
    This test verifies that the `get_env_as_dict` returns the contents of a
    valid spack manifest file in dictionary form.
    """
    manifest = os.path.join(tmpdir.strpath, "env", "spack.yaml")
    data = create_spack_manifest(manifest)

    env = spack.environment.environment_from_name_or_dir(os.path.dirname(manifest))
    assert distribution.get_env_as_dict(env) == data


def test_get_local_config(tmpdir):
    """
    This test verifies that the `get_local_config` returns the contents
    of a valid set spack YAML files in dictionary form when given a
    directory containing those files.
    """
    exclude_dir = os.path.join(tmpdir.strpath, "dir")
    packages = os.path.join(exclude_dir, "packages.yaml")
    data = create_pacakge_manifest(packages)

    repos = os.path.join(exclude_dir, "repos.yaml")
    repo_data = {"repos": {"name": "/path/to/repo"}}
    with open(repos, "w") as f:
        spack.util.spack_yaml.dump(repo_data, f, default_flow_style=False)

    result = distribution.get_local_config(exclude_dir)
    expected = data.copy()
    expected.update(repo_data)
    assert result == expected


def test_get_valid_env_scopes(tmpdir):
    """
    This test verifies that `valid_env_scopes` returns a resonable set of
    spack config scopes. `valid_env_scopes` defines the possible set of scopes
    from which the distribution module expects to grab data
    (the environemnt and any included scope)
    """
    manifest = os.path.join(tmpdir.strpath, "env", "spack.yaml")
    packages = os.path.join(tmpdir.strpath, "dir", "packages.yaml")

    extra_data = {"include": [os.path.dirname(packages)]}
    create_spack_manifest(manifest, extra_data=extra_data)
    create_pacakge_manifest(packages)

    env = spack.environment.environment_from_name_or_dir(os.path.dirname(manifest))
    with env:
        scope_names = distribution.valid_env_scopes(env)
    assert len(scope_names) == 2


class MockArgs:
    def __init__(self, source=False, binary=False):
        self.source_only = source
        self.binary_only = binary


class MockEnv:
    def __init__(self, specs):
        self.specs = [(x, f"{x}.concrete") for x in specs]

    def concretized_specs(self):
        return self.specs


def mock_verification(arg):
    class MockVerify:
        def __init__(self, arg):
            self.errors = "error" in arg

        def has_errors(self):
            return self.errors

    return MockVerify(arg)


def test_correct_mirror_args_does_not_modify_args_when_source_only():
    """
    This test verifies that `correct_mirror_args` does nothing if source_only was requested.
    """
    args = MockArgs(source=True)
    env = MockEnv(["hdf5"])

    assert args.source_only
    assert not args.binary_only
    distribution.correct_mirror_args(env, args)
    assert args.source_only
    assert not args.binary_only


def test_correct_mirror_args_does_sets_source_only_if_no_concretized_specs_in_env():
    """
    This test verifies that `correct_mirror_args` reverts to source_only if binaries aren't in env.
    """
    args = MockArgs()
    env = MockEnv([])

    assert not args.source_only
    assert not args.binary_only
    distribution.correct_mirror_args(env, args)
    assert args.source_only
    assert not args.binary_only


def test_correct_mirror_args_does_sets_source_only_if_install_not_verified(monkeypatch):
    """
    This test verifies that `correct_mirror_args` reverts to source_only if binaries aren't
    verified as correct.
    """
    args = MockArgs()
    env = MockEnv(["hdf5.error"])

    monkeypatch.setattr(spack.verify, "check_spec_manifest", mock_verification)
    assert not args.source_only
    assert not args.binary_only
    distribution.correct_mirror_args(env, args)
    assert args.source_only
    assert not args.binary_only


def test_correct_mirror_args_does_no_modification_if_install_verified(monkeypatch):
    """
    This test verifies that `correct_mirror_args` does nothing if binaries exist.
    """
    args = MockArgs()
    env = MockEnv(["hdf5.valid"])

    monkeypatch.setattr(spack.verify, "check_spec_manifest", mock_verification)
    assert not args.source_only
    assert not args.binary_only
    distribution.correct_mirror_args(env, args)
    assert not args.source_only
    assert not args.binary_only


def test_correct_mirror_args_does_errors_if_binary_only_but_no_binaries_exist(monkeypatch):
    """
    This test verifies that `correct_mirror_args` errors out if binary_only
    is True and source_only gets defaulted to True.
    """
    args = MockArgs(binary=True)
    env = MockEnv(["hdf5.error"])

    monkeypatch.setattr(spack.verify, "check_spec_manifest", mock_verification)
    assert not args.source_only
    assert args.binary_only

    with pytest.raises(SystemExit):
        distribution.correct_mirror_args(env, args)


def test_DistributionPackager_init_distro_dir(tmpdir):
    """
    This test verifies that `init_distro_dir` correctly creates a directory
    for the distribution to be packaged. If the directory already exists,
    the test asserts that the contents are wiped and the directory is re-created.
    """
    root = os.path.join(tmpdir.strpath, "root")

    pkgr = distribution.DistributionPackager(None, root)
    assert not os.path.isdir(root)
    pkgr.init_distro_dir()
    assert os.path.isdir(root)
    test_file = os.path.join(root, "test")
    with open(test_file, "w") as outf:
        outf.write("content")
    assert os.path.isfile(test_file)
    pkgr.init_distro_dir()
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


def test_DistributionPackager_filter_excludes_no_excludes(tmpdir):
    """
    This test verifies that `filter_excludes` does not modify the existing
    environment when no excludes are passed.
    """
    root = os.path.join(tmpdir.strpath, "root")
    manifest = os.path.join(root, "environment", "spack.yaml")
    extra_data = {"packages": {"gcc": {"require": ["@1.2.3"]}}}
    create_spack_manifest(manifest, extra_data=extra_data)
    env_dir = os.path.dirname(manifest)
    env = get_fake_concretize_env(env_dir)

    pkgr = distribution.DistributionPackager(None, root)
    pkgr._env = env
    pkgr.filter_excludes()

    content = get_manifest(pkgr.env)
    assert "packages" in content["spack"]
    assert "specs" in content["spack"]


def test_DistributionPackager_filter_excludes_with_excludes(tmpdir):
    """
    This test verifies that `filter_excludes` correctly modifies the environment
    when an exclude dir is passed.
    """
    root = os.path.join(tmpdir.strpath, "root")
    exclude_dir = os.path.join(tmpdir.strpath, "excludes")
    exclude_file = os.path.join(exclude_dir, "packages.yaml")
    os.makedirs(exclude_dir)
    data = {"packages": {"gcc": {}}}
    with open(exclude_file, "w") as outf:
        spack.util.spack_yaml.dump(data, outf, default_flow_style=False)
    manifest = os.path.join(root, "environment", "spack.yaml")
    extra_data = {"packages": {"gcc": {"require": ["@1.2.3"]}}}
    create_spack_manifest(manifest, extra_data=extra_data)
    env_dir = os.path.dirname(manifest)
    env = get_fake_concretize_env(env_dir)

    pkgr = distribution.DistributionPackager(None, root, excludes=exclude_dir)
    pkgr._env = env
    pkgr.filter_excludes()

    content = get_manifest(pkgr.env)
    assert "packages" not in content["spack"]
    assert "specs" in content["spack"]


def test_concretzie(tmpdir):
    """
    This test verifies that `concretize` method calls env.concretize() on the
    environment being created.
    """
    root = os.path.join(tmpdir.strpath, "root")
    manifest = os.path.join(root, "environment", "spack.yaml")
    create_spack_manifest(manifest)
    env_dir = os.path.dirname(manifest)
    env = get_fake_concretize_env(env_dir)

    pkgr = distribution.DistributionPackager(None, root)
    pkgr._env = env

    pkgr.concretize()
    lockfile = os.path.join(env_dir, "spack.lock")
    assert os.path.isfile(lockfile)


def test_DistributionPackager_remove_unwanted_artifacts(tmpdir):
    """
    This test verifies that `remove_unwanted_artifacts` removes files
    created by concretizing the environment.
    """
    root = os.path.join(tmpdir.strpath, "root")
    manifest = os.path.join(root, "environment", "spack.yaml")
    create_spack_manifest(manifest)
    env_dir = os.path.dirname(manifest)
    env = get_fake_concretize_env(env_dir)

    pkgr = distribution.DistributionPackager(None, root)
    pkgr._env = env

    pkgr.concretize()
    assert len(os.listdir(env_dir)) == 3
    pkgr.remove_unwanted_artifacts()
    env_assets = os.listdir(env_dir)
    assert len(env_assets) == 1
    assert "spack.yaml" in env_assets


def test_DistributionPackager_configure_includes(tmpdir):
    """
    This test verifies that `configure_includes` copies a directory of
    yaml files to be included in the environment into the environment
    being created and adds a relative path to the copied directory to
    the spack.yaml that is being constructed.
    """
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
    """
    This test verifies that `configure_specs` adds all specs in the current
    environment to the environment being created
    """
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
    """
    This test verifies that `configure_extensions` copies any extensions
    defined in the current environment into the environment being created
    and adds a relative path to the copied extension to the spack.yaml that
    is being constructed.
    """
    root = os.path.join(tmpdir.strpath, "root")
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    extensions = [
        os.path.join(tmpdir.strpath, "extensions", "spack-extensiona"),
        os.path.join(tmpdir.strpath, "extensions", "spack-extensionb"),
    ]
    expected_extensions = [os.path.join("..", "extensions", "spack-manager")]
    for ext in extensions:
        expected_extensions.append(os.path.join("..", "extensions", os.path.basename(ext)))
        create_extension(ext)

    extra_data = {"config": {"extensions": extensions}}
    create_spack_manifest(manifest, extra_data=extra_data)
    env = spack.environment.Environment(os.path.dirname(manifest))

    pkgr = distribution.DistributionPackager(env, root)
    content = get_manifest(pkgr.env)
    assert "extensions" not in content["spack"].get("config", {})
    for extension in expected_extensions:
        assert not os.path.isdir(extension)

    with tmpdir.as_cwd():
        pkgr.configure_extensions()
    mod_content = get_manifest(pkgr.env)
    print("content", mod_content)

    for extension in expected_extensions:
        assert os.path.isdir(os.path.join(pkgr.env.path, extension))
    assert "extensions" in mod_content["spack"].get("config", {})
    assert set(mod_content["spack"]["config"]["extensions"]) == set(expected_extensions)


def test_DistributionPackager_configure_repos(tmpdir):
    """
    This test verifies that `configure_repos` copies all package repositories defined in
    the environment into the environment being created and adds a relative path to the
    copied repositories to the spack.yaml that is being constructed.
    """
    package_repo = os.path.join(tmpdir.strpath, "mock-repo")
    create_repo(package_repo)

    extra_data = {"repos": {"mock-repo": package_repo}}
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest, extra_data=extra_data)
    env = spack.environment.Environment(os.path.dirname(manifest))

    root = os.path.join(tmpdir.strpath, "root")
    pkgr = distribution.DistributionPackager(env, root)

    expected_repo_dir = os.path.join(pkgr.package_repos, os.path.basename(package_repo))
    initial_config = get_manifest(pkgr.env)
    assert not os.path.isdir(expected_repo_dir)
    assert "repos" not in initial_config["spack"]
    pkgr.configure_package_repos()
    result_config = get_manifest(pkgr.env)
    assert os.path.isdir(expected_repo_dir)
    assert "repos" in result_config["spack"]

    expected_repo = {"mock-repo": f"../{os.path.basename(pkgr.package_repos)}/mock-repo"}
    assert expected_repo == result_config["spack"]["repos"]


def test_DistributionPackager_configure_package_settings(tmpdir):
    """
    This test verifies that `configure_package_settings` copies the contents of
    the `packages` scope from the current environment to the environment being copied.
    This test asserts that all packages are copied if `filter_externals` is `False`
    and that any packages defined as `external` are excluded from the new environment
    when `filter_externals` is `True`.
    """
    good = {"all": {"prefer": ["generator=Ninja"]}}
    bad = {"cmake": {"externals": [{"spec": "cmake@1.2.3", "path": "/foo/bar"}]}}

    extra_data = {"packages": {}}
    extra_data["packages"].update(good)
    extra_data["packages"].update(bad)
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest, extra_data=extra_data)
    env = spack.environment.Environment(os.path.dirname(manifest))
    root = os.path.join(tmpdir.strpath, "root")

    pkgr = distribution.DistributionPackager(env, root)

    inital_config = get_manifest(pkgr.env)
    assert "packages" not in inital_config["spack"]
    pkgr.configure_package_settings(filter_externals=True)
    result_config = get_manifest(pkgr.env)
    assert "packages" in result_config["spack"]
    assert good == result_config["spack"]["packages"]

    pkgr.configure_package_settings(filter_externals=False)
    new_result_config = get_manifest(pkgr.env)
    new_expected = good.copy()
    new_expected.update(bad)
    assert new_expected == new_result_config["spack"]["packages"]


def test_DistributionPackager_bundle_extra_data(tmpdir):
    """
    This test verifies that `bundle_extra_data` recursively copies the contents of the the
    `extra_data` path into the root of the distro dir being created.
    """
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
    """
    This test verifies that `DistributionPackager` correctly configures its final state on exit.
    """
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
    """
    This test verifies that `DistributionPackager` correctly configures inital state on entry.
    """
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


def test_DistributionPackager_configure_source_mirror_create_mirror_called_correctly(
    tmpdir, monkeypatch
):
    """
    This test verifies that `configure_source_mirror` does not construct a call to
    `create_mirror_for_all_specs` that violates its API.
    """
    valid_params = inspect.signature(distribution.create_mirror_for_all_specs).parameters.keys()

    def mirror_for_specs(*args, **kwargs):
        assert len(args) == 0
        assert len(kwargs) == len(valid_params)
        for kwarg in kwargs:
            assert kwarg in valid_params

    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest)
    env = get_fake_concretize_env(os.path.dirname(manifest))
    root = os.path.join(tmpdir.strpath, "root")
    pkgr = distribution.DistributionPackager(env, root)

    monkeypatch.setattr(distribution, "create_mirror_for_all_specs", mirror_for_specs)
    pkgr.configure_source_mirror()

    content = get_manifest(pkgr.env)
    expected = {"internal-source": "../source-mirror"}
    assert "mirrors" in content["spack"]
    assert content["spack"]["mirrors"] == expected


def test_DistributionPackager_configure_source_mirror_created_in_correct_sequence(
    tmpdir, monkeypatch
):
    """
    This test verifies that `configure_source_mirror` correctly constructs the source mirror.
    Because of nuances of when access is available to source code that is access-controlled,
    the source mirror must be created using two calls under specific conditions.  This test
    validates the call sequence is correct.
    """
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest)
    env = spack.environment.Environment(os.path.dirname(manifest))
    root = os.path.join(tmpdir.strpath, "root")
    pkgr = distribution.DistributionPackager(env, root)

    class Mock:
        envs = [pkgr.env.path, env.path]

        @classmethod
        def mirror_for_specs(cls, *args, **kwargs):
            assert spack.environment.active_environment().path == cls.envs.pop()

    monkeypatch.setattr(distribution, "create_mirror_for_all_specs", Mock.mirror_for_specs)
    pkgr.configure_source_mirror()

    assert Mock.envs == []


def test_DistributionPackager_configure_source_mirror_mirror_added_to_env(tmpdir, monkeypatch):
    """
    This test verifies that `configure_source_mirror` adds a relative path to the created
    mirror to the new environment.
    """

    def mirror_for_specs(*args, **kwargs):
        pass

    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest)
    env = spack.environment.Environment(os.path.dirname(manifest))
    root = os.path.join(tmpdir.strpath, "root")
    pkgr = distribution.DistributionPackager(env, root)

    monkeypatch.setattr(distribution, "create_mirror_for_all_specs", mirror_for_specs)
    pkgr.configure_source_mirror()

    content = get_manifest(pkgr.env)
    assert "mirrors" in content["spack"]
    assert content["spack"]["mirrors"] == {"internal-source": "../source-mirror"}


def test_DistributionPackager_configure_bootstrap_mirror(tmpdir, monkeypatch):
    """
    This test verifies that `configure_bootstrap_mirror` does not construct a call to
    `spack bootstrap` that violates its API.
    """
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest)
    env = spack.environment.Environment(os.path.dirname(manifest))
    root = os.path.join(tmpdir.strpath, "root")
    pkgr = distribution.DistributionPackager(env, root)

    class MockCommand:
        args = []
        kwargs = {}
        call_args = []

        def __init__(self, *args, **kwargs):
            self.args += list(args)
            self.kwargs.update(kwargs)

        def __call__(self, *args, **kwargs):
            self.call_args.append(list(args))
            self.kwargs.update(kwargs)

    monkeypatch.setattr(distribution, "SpackCommand", MockCommand)
    pkgr.configure_bootstrap_mirror()

    assert MockCommand.args == ["bootstrap"]
    assert MockCommand.kwargs == {}
    assert len(MockCommand.call_args) == 3

    parser = ArgumentParser()
    test_bootstrap_parse.setup_parser(parser)
    with pkgr.env:
        for call in MockCommand.call_args:
            parser.parse_args(call)


def test_DistributionPackager_configure_binary_mirror(tmpdir, monkeypatch):
    """
    This test verifies that `configure_binary_mirror` does not construct a call to
    `spack buildcache` or `spack mirror` that violates its API.
    """
    manifest = os.path.join(tmpdir.strpath, "base-env", "spack.yaml")
    create_spack_manifest(manifest)
    env = spack.environment.Environment(os.path.dirname(manifest))
    root = os.path.join(tmpdir.strpath, "root")
    pkgr = distribution.DistributionPackager(env, root)

    class MockCommand:
        args = []
        kwargs = {}
        call_args = []

        def __init__(self, *args, **kwargs):
            self.args += list(args)
            self.kwargs.update(kwargs)

        def __call__(self, *args, **kwargs):
            self.call_args.append(list(args))
            self.kwargs.update(kwargs)

    monkeypatch.setattr(distribution, "SpackCommand", MockCommand)
    pkgr.configure_binary_mirror()

    assert MockCommand.args == ["buildcache", "mirror"]
    assert MockCommand.kwargs == {}
    assert len(MockCommand.call_args) == 2

    buildcache_parser = ArgumentParser()
    test_buildcache_parse.setup_parser(buildcache_parser)
    mirror_parser = ArgumentParser()
    test_mirror_parse.setup_parser(mirror_parser)
    with pkgr.env:
        buildcache_parser.parse_args(MockCommand.call_args[0])
        mirror_parser.parse_args(MockCommand.call_args[1])
