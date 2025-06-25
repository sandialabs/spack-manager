# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import re

import spack.main
from spack.extensions.manager.manager_cmds.location import location
from spack.util.path import canonicalize_path as spack_path_resolve

arch = spack.main.SpackCommand("arch")


def canonicalize_path(path, default_wd=None):
    """
    wrapper around spack's path expansion to add our own variables
    wouldn't be too hard to allow natural extension of spack's core command
    """
    _replacements = {"spack_manager": lambda: location()}

    # Look up replacements
    def repl(match):
        m = match.group(0)
        key = m.strip("${}").lower()
        repl = _replacements.get(key, lambda: m)()
        return m if repl is object() else str(repl)

    # Replace $var or ${var}.
    path = re.sub(r"(\$\w+\b|\$\{\w+\})", repl, path)
    return spack_path_resolve(path, default_wd=default_wd)


def pruned_spec_string(spec, variants_to_omit=["ipo", "dev_path=", "patches=", "build_system="]):
    full_spec = spec.format("{name}{@version}{variants}{%compiler}")

    # add spaces between variants so we can filter
    spec_components = full_spec.replace("+", " +").replace("%", " %").replace("~", " ~").split(" ")

    def filter_func(entry):
        for v in variants_to_omit:
            if v in entry:
                return False
        return True

    pruned_components = list(filter(filter_func, spec_components))

    pruned_spec = " ".join(pruned_components)
    return pruned_spec


def command(command, *args):
    """
    Execute a spack.main.SpackCommand uniformly
    and add some print statements
    """
    print("spack", command.command_name, *args)
    print(command(*args, fail_on_error=False))
