# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import functools
import inspect

import spack.binary_distribution as bindist
import spack.cmd
import spack.cmd.find
import spack.config


def setup_parser_args(sub_parser):
    spack.cmd.find.setup_parser(sub_parser)


def _binary_cache_query():
    # Newer Spack requires the configuration to be passed explicitly
    if "config" in inspect.signature(bindist.BinaryCacheQuery.__init__).parameters:
        return bindist.BinaryCacheQuery(True, config=spack.config.CONFIG)
    return bindist.BinaryCacheQuery(True)


def cache_search(self, **kwargs):
    # spack version splits
    if hasattr(self, "values"):
        data = getattr(self, "values")
    else:
        data = getattr(self, "constraint")
    qspecs = spack.cmd.parse_specs(data)
    search_engine = _binary_cache_query()
    results = {}
    for q in qspecs:
        hits = search_engine(str(q), **kwargs)
        for hit in hits:
            results[hit.dag_hash()] = hit
    return sorted(results.values())


def cache_query(parser, args):
    # Only override spec lookup for this command so other commands (e.g. module refresh)
    # still query installed specs instead of the binary cache
    args.specs = functools.partial(cache_search, args)
    spack.cmd.find.find(parser, args)


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "cache-query",
        help=(
            "forwarding spack find to allow buildcaches quiries."
            " warning, not all flags are supported"
        ),
    )
    setup_parser_args(sub_parser)
    command_dict["cache-query"] = cache_query
