# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import sys

import llnl.util.tty as tty

import spack.cmd as cmd
import spack.cmd.find as sfind
import spack.environment as ev
import spack.binary_distribution as bindist

import spack.cmd.common.arguments
import spack.repo
from spack.database import InstallStatuses


def setup_parser_args(sub_parser):
    sfind.setup_parser(sub_parser)


def cache_search(self, **kwargs):
    qspecs = spack.cmd.parse_specs(self.values)
    search_engine = bindist.BinaryCacheQuery(True)
    results = {}
    for q in qspecs:
        hits = search_engine(str(q), **kwargs)
        for hit in hits:
            results[hit.dag_hash()] = hit
    return sorted(results.values())

spack.cmd.common.arguments.ConstraintAction._specs = cache_search

def cache_query(parser, args):
    q_args = sfind.query_arguments(args)
    results = args.specs(**q_args)

    env = ev.active_environment()
    decorator = lambda s, f: f
    if env:
        decorator, _, roots, _ = setup_env(env)

    # use groups by default except with format.
    if args.groups is None:
        args.groups = not args.format

    # Exit early with an error code if no package matches the constraint
    if not results and args.constraint:
        msg = "No package matches the query: {0}"
        msg = msg.format(" ".join(args.constraint))
        tty.msg(msg)
        raise SystemExit(1)

    # If tags have been specified on the command line, filter by tags
    if args.tags:
        packages_with_tags = spack.repo.path.packages_with_tags(*args.tags)
        results = [x for x in results if x.name in packages_with_tags]

    if args.loaded:
        results = spack.cmd.filter_loaded_specs(results)

    # Display the result
    if args.json:
        cmd.display_specs_as_json(results, deps=args.deps)
    else:
        if not args.format:
            if env:
                display_env(env, args, decorator, results)

        cmd.display_specs(results, args, decorator=decorator, all_headers=True)

        # print number of installed packages last (as the list may be long)
        if sys.stdout.isatty() and args.groups:
            pkg_type = "loaded" if args.loaded else "installed"
            spack.cmd.print_how_many_pkgs(results, pkg_type)


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
            "cache-query", help="query buildcaches"
    )
    setup_parser_args(sub_parser)
    command_dict["cache-query"] = cache_query
