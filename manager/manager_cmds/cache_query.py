# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import spack.cmd
import spack.cmd.find

import spack.cmd.common.arguments as arguments
import spack.binary_distribution as bindist


def setup_parser_args(sub_parser):
    spack.cmd.find.setup_parser(sub_parser)


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
    spack.cmd.find.find(parser, args)


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
            "cache-query", help="query buildcaches"
    )
    setup_parser_args(sub_parser)
    command_dict["cache-query"] = cache_query
