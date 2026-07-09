import concurrent.futures
import json
import os
import re
import sys
import time
from contextlib import contextmanager
from functools import partial

import spack
import spack.builder
from spack import environment

"""
This extension was contributed by vbrunini
"""


command_name = "compile-commands"
description = (
    "Copy compile_commands.json for all develop packages in the active environment,"
    " then remove cross-package -isystem flags and substitute source/build -I flags."
)
section = "sierra"
level = "long"
aliases = []


def setup_parser(subparser):
    subparser.add_argument(
        "--serial", action="store_true", help="Process compile_commands.json files in serial."
    )


@contextmanager
def timer(name: str, args):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    if args.verbose:
        print(f"[{name}] elapsed: {end-start:.3f} s")


def build_dir(builder, pkg):
    if hasattr(builder, "build_directory"):
        return os.path.normpath(os.path.join(pkg.stage.path, builder.build_directory))
    return pkg.stage.source_path


def source_root(pkg):
    if hasattr(pkg, "root_cmakelists_dir"):
        return os.path.join(pkg.stage.source_path, pkg.root_cmakelists_dir)
    return pkg.stage.source_path


def _process_spec(spec, args):
    """Worker that handles a single spec and returns (info, (regex, includes))."""

    if not spec.is_develop:
        return None

    pkg = spec.package
    if args.verbose:
        sys.stdout.write(f"\nProcessing {pkg.name}\n")
    try:
        builder = spack.builder.create(pkg)
        src_cc_path = os.path.join(build_dir(builder, pkg), "compile_commands.json")
    except Exception:
        return None

    if not os.path.exists(src_cc_path):
        return None

    dst_dir = pkg.stage.source_path
    if getattr(pkg, "root_cmakelists_dir", None):
        dst_dir = os.path.join(dst_dir, pkg.root_cmakelists_dir)
    os.makedirs(dst_dir, exist_ok=True)
    dest_cc_path = os.path.join(dst_dir, "compile_commands.json")

    if os.path.islink(dest_cc_path):
        if args.verbose:
            sys.stdout.write(f"  removing existing symlink {dest_cc_path}\n")
        os.unlink(dest_cc_path)

    try:
        with open(src_cc_path) as f:
            cc_entries = json.load(f)
    except Exception:
        cc_entries = []

    pkg_build_dir = build_dir(builder, pkg)
    pkg_src_root = source_root(pkg)

    source_include_flags = []
    source_include_re = re.compile(rf"-I(?:{pkg_src_root}|{pkg_build_dir})\S*")
    for entry in cc_entries:
        if "command" not in entry:
            continue
        for match in source_include_re.findall(entry["command"]):
            if match not in source_include_flags:
                source_include_flags.append(match)

    replacement_pattern = rf"-isystem\s+{pkg.prefix}\S*"
    if args.verbose:
        sys.stdout.write(f"  replacement pattern = {replacement_pattern}\n")
        sys.stdout.write(f"  source include flags = {source_include_flags}\n")

    info = {"cc_entries": cc_entries, "dest_cc_path": dest_cc_path}
    repl = (re.compile(replacement_pattern), " ".join(source_include_flags))
    return (info, repl)


def _apply_replacements(info, include_path_replacements):
    cc_entries = info["cc_entries"]
    dest_cc_path = info["dest_cc_path"]

    for entry in cc_entries:
        if "command" not in entry:
            continue
        command = entry["command"]
        for regex, source_includes in include_path_replacements:
            # First replace with the gathered -I flags, then strip any leftover -isystem
            command = regex.sub(source_includes, command, 1)
            command = regex.sub("", command)
        entry["command"] = command

    # Write out the (now cleaned) compile_commands.json
    with open(dest_cc_path, "w") as f:
        json.dump(cc_entries, f, indent=2)
        f.write("\n")
    return dest_cc_path


def _get_executor(args):
    if args.serial:
        return concurrent.futures.ThreadPoolExecutor(max_workers=1)

    return concurrent.futures.ProcessPoolExecutor()


def compile_commands(parser, args):
    env = environment.active_environment()

    # First pass: copy each compile_commands.json into its source dir
    infos = []
    include_path_replacements = []
    with timer("Determine include path replacements", args):
        with _get_executor(args) as exe:
            futures = [exe.submit(_process_spec, spec, args) for spec in env.all_specs()]
            for fut in concurrent.futures.as_completed(futures):
                result = fut.result()
                if result is None:
                    continue
                info, repl = result
                infos.append(info)
                include_path_replacements.append(repl)

    # Second pass: Apply isystem removal regexes and insert corresponding source include flags if
    # they were applied
    with timer("Apply include path replacements", args):
        with _get_executor(args) as exe:
            list(
                exe.map(
                    partial(
                        _apply_replacements, include_path_replacements=include_path_replacements
                    ),
                    infos,
                )
            )


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        command_name, help=description, description=description, aliases=aliases
    )
    setup_parser(sub_parser)
    command_dict[command_name] = compile_commands
    for alias in aliases:
        command_dict[alias] = compile_commands
