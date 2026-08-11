import json
import os
import shlex
from unittest import mock

import pytest

import spack.builder
import spack.environment
import spack.main

manager = spack.main.SpackCommand("manager")


class DummyPkg:
    def __init__(self, name, build_root, src_root, prefix, root_cmakelists_dir=None):
        self.name = name
        self.stage = mock.Mock()
        self.stage.path = str(build_root)
        self.stage.source_path = str(src_root)
        self.prefix = str(prefix)
        if root_cmakelists_dir is not None:
            self.root_cmakelists_dir = root_cmakelists_dir


class DummyBuilder:
    def __init__(self, build_directory):
        self.build_directory = build_directory


@pytest.fixture
def mock_environment_and_package(tmp_path, monkeypatch):
    """
    Single‐package fixture, with root_cmakelists_dir='bar'.
    Yields (pkg, path_to_original_compile_commands.json).
    """
    build_root = tmp_path / "build"
    src_root = tmp_path / "source"
    inst_root = tmp_path / "install"

    # make build_dir and source/bar
    (build_root / "build_dir").mkdir(parents=True)
    (src_root / "bar").mkdir(parents=True)
    inst_root.mkdir()

    # write an empty compile_commands.json in build_dir
    cc_in = build_root / "build_dir" / "compile_commands.json"
    with open(cc_in, "w") as f:
        f.write("{}")

    # create pkg/spec/env
    pkg = DummyPkg("foo", build_root, src_root, inst_root, root_cmakelists_dir="bar")
    spec = mock.Mock(package=pkg)
    fake_env = mock.Mock(all_specs=mock.Mock(return_value=[spec]))

    # patch active_environment() and builder.create(...)
    monkeypatch.setattr(spack.environment, "active_environment", lambda: fake_env)
    monkeypatch.setattr(spack.builder, "create", lambda pkg: DummyBuilder("build_dir"))

    return pkg, str(cc_in)


def test_compile_commands_copies_file(mock_environment_and_package):
    pkg, cc_in = mock_environment_and_package
    manager("compile-commands", "--serial")
    dest = os.path.join(pkg.stage.source_path, "bar", "compile_commands.json")
    assert os.path.exists(dest)

    # cleanup
    os.remove(cc_in)
    os.remove(dest)
    os.rmdir(os.path.dirname(cc_in))


def test_compile_commands_symlink_replacement(mock_environment_and_package):
    pkg, cc_in = mock_environment_and_package
    dest = os.path.join(pkg.stage.source_path, "bar", "compile_commands.json")

    # create a symlink at the destination
    os.symlink("/some/other/path", dest)
    manager("compile-commands", "--serial")

    assert os.path.exists(dest)
    assert not os.path.islink(dest)

    # cleanup
    os.remove(cc_in)
    os.remove(dest)
    os.rmdir(os.path.dirname(cc_in))


def test_compile_commands_no_source_file(tmp_path, monkeypatch):
    # pkg with no compile_commands.json in build_dir
    build_root = tmp_path / "build"
    src_root = tmp_path / "source"
    inst_root = tmp_path / "install"

    (src_root / "bar").mkdir(parents=True)
    inst_root.mkdir()

    pkg = DummyPkg("foo", build_root, src_root, inst_root, root_cmakelists_dir="bar")
    spec = mock.Mock(package=pkg)
    fake_env = mock.Mock(all_specs=mock.Mock(return_value=[spec]))

    monkeypatch.setattr(spack.environment, "active_environment", lambda: fake_env)
    monkeypatch.setattr(spack.builder, "create", lambda pkg: DummyBuilder("build_dir"))

    manager("compile-commands", "--serial")
    dest = os.path.join(pkg.stage.source_path, "bar", "compile_commands.json")
    assert not os.path.exists(dest)


def test_compile_commands_no_root_cmakelists_dir(mock_environment_and_package):
    pkg, cc_in = mock_environment_and_package
    # remove the attribute
    if hasattr(pkg, "root_cmakelists_dir"):
        del pkg.root_cmakelists_dir

    manager("compile-commands", "--serial")
    dest = os.path.join(pkg.stage.source_path, "compile_commands.json")
    assert os.path.exists(dest)

    # cleanup
    os.remove(cc_in)
    os.remove(dest)
    os.rmdir(os.path.dirname(cc_in))


@pytest.fixture
def two_pkg_env(tmp_path, monkeypatch):
    """
    Two‐package fixture: pkg_foo and pkg_bar,
    each with a compile_commands.json in build_dir.
    bar’s file refers via -isystem to something under foo.prefix.
    """
    # foo
    build_foo = tmp_path / "build_foo"
    (build_foo / "build_dir").mkdir(parents=True)
    src_foo = tmp_path / "src_foo"
    src_foo.mkdir()
    inst_foo = tmp_path / "inst_foo"
    inst_foo.mkdir()
    (src_foo / "inc").mkdir()
    (build_foo / "build_dir" / "bld_inc").mkdir(parents=True)

    foo_cmd = "clang -I{} -I{} -c foo.c".format(
        src_foo / "inc", build_foo / "build_dir" / "bld_inc"
    )
    foo_entries = [{"directory": str(build_foo), "command": foo_cmd, "file": "foo.c"}]
    foo_cc = build_foo / "build_dir" / "compile_commands.json"
    with open(foo_cc, "w") as f:
        json.dump(foo_entries, f)

    # bar
    build_bar = tmp_path / "build_bar"
    (build_bar / "build_dir").mkdir(parents=True)
    src_bar = tmp_path / "src_bar"
    src_bar.mkdir()
    inst_bar = tmp_path / "inst_bar"
    inst_bar.mkdir()

    # create an include dir under foo’s install prefix
    foo_inc_inst = inst_foo / "foo_inc_dir"
    foo_inc_inst.mkdir()

    bar_cmd = (
        f"clang -I{src_bar} -isystem {foo_inc_inst} -isystem {foo_inc_inst}/subdir_1 "
        "-isystem {foo_inc_inst}/subdir_2 -c bar.c"
    )
    bar_entries = [{"directory": str(build_bar), "command": bar_cmd, "file": "bar.c"}]
    bar_cc = build_bar / "build_dir" / "compile_commands.json"
    with open(bar_cc, "w") as f:
        json.dump(bar_entries, f)

    # create pkgs/specs/env
    pkg_foo = DummyPkg("foo", build_foo, src_foo, inst_foo)
    pkg_bar = DummyPkg("bar", build_bar, src_bar, inst_bar)
    spec_foo = mock.Mock(package=pkg_foo)
    spec_bar = mock.Mock(package=pkg_bar)
    fake_env = mock.Mock(all_specs=mock.Mock(return_value=[spec_foo, spec_bar]))

    monkeypatch.setattr(spack.environment, "active_environment", lambda: fake_env)
    monkeypatch.setattr(spack.builder, "create", lambda pkg: DummyBuilder("build_dir"))

    return pkg_foo, pkg_bar


def test_strip_isystem_and_inject_I(two_pkg_env):
    pkg_foo, pkg_bar = two_pkg_env
    manager("compile-commands", "--serial")

    # foo’s file unchanged (except no -isystem):
    foo_dst = os.path.join(pkg_foo.stage.source_path, "compile_commands.json")
    data = json.load(open(foo_dst))
    toklist = shlex.split(data[0]["command"])
    assert "-I" + os.path.join(pkg_foo.stage.source_path, "inc") in toklist
    assert "-I" + os.path.join(pkg_foo.stage.path, "build_dir", "bld_inc") in toklist
    assert all(not t.startswith("-isystem") for t in toklist)

    # bar’s file: -isystem removed, foo’s -I flags injected
    bar_dst = os.path.join(pkg_bar.stage.source_path, "compile_commands.json")
    data = json.load(open(bar_dst))
    toklist = shlex.split(data[0]["command"])
    assert all(not t.startswith("-isystem") for t in toklist)
    assert "-I" + os.path.join(pkg_foo.stage.source_path, "inc") in toklist
    assert "-I" + os.path.join(pkg_foo.stage.path, "build_dir", "bld_inc") in toklist
    assert "-I" + os.path.join(pkg_foo.stage.source_path, "inc") in toklist


def test_no_cross_inject_when_no_isystem(tmp_path, monkeypatch):
    # Build two packages, each only with its own -I under source
    build1 = tmp_path / "b1"
    (build1 / "build_dir").mkdir(parents=True)
    src1 = tmp_path / "s1"
    src1.mkdir()
    inst1 = tmp_path / "i1"
    inst1.mkdir()
    inc1 = src1 / "inc1"
    inc1.mkdir()
    cc1 = build1 / "build_dir" / "compile_commands.json"
    with open(cc1, "w") as f:
        json.dump([{"directory": str(build1), "command": f"cc -I{inc1} -c a.c", "file": "a.c"}], f)

    build2 = tmp_path / "b2"
    (build2 / "build_dir").mkdir(parents=True)
    src2 = tmp_path / "s2"
    src2.mkdir()
    inst2 = tmp_path / "i2"
    inst2.mkdir()
    inc2 = src2 / "inc2"
    inc2.mkdir()
    cc2 = build2 / "build_dir" / "compile_commands.json"
    with open(cc2, "w") as f:
        json.dump([{"directory": str(build2), "command": f"cc -I{inc2} -c b.c", "file": "b.c"}], f)

    pkg1 = DummyPkg("one", build1, src1, inst1)
    pkg2 = DummyPkg("two", build2, src2, inst2)
    spec1 = mock.Mock(package=pkg1)
    spec2 = mock.Mock(package=pkg2)
    fake_env = mock.Mock(all_specs=mock.Mock(return_value=[spec1, spec2]))

    monkeypatch.setattr(spack.environment, "active_environment", lambda: fake_env)
    monkeypatch.setattr(spack.builder, "create", lambda pkg: DummyBuilder("build_dir"))

    manager("compile-commands", "--serial")

    for pkg in (pkg1, pkg2):
        dst = os.path.join(pkg.stage.source_path, "compile_commands.json")
        data = json.load(open(dst))
        toks = shlex.split(data[0]["command"])
        # must have its own -I but no -isystem, and no other injections
        assert any(t.startswith("-I" + pkg.stage.source_path) for t in toks)
        assert all(not t.startswith("-isystem") for t in toks)
