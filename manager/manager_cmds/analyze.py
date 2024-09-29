# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
import json
import os
import statistics
import sys

import spack.deptypes as dt
import spack.traverse
from spack.graph import DotGraphBuilder

command_name = "analyze"
description = "tooling for analyzing statistics of the DAG"
aliases = []


def setup_parser_args(subparser):
    subparser.add_argument(
        "--decay-points", nargs="+", help="sources for a subgraph that traces back to the root"
    )


def get_timings(spec):
    if spec.installed:
        timing_files = spec.package.times_log_path
        if os.path.isfile(timing_files):
            with open(timing_files, "r") as f:
                spec_data = json.load(f)
                # extract phases
                output = {}
                for phase in spec_data["phases"]:
                    output[phase["name"]] = phase["seconds"]
                return output
    return None


def compute_dag_stats(specs, direction="children", depflag=dt.ALL):
    dag_data = {}
    for edge in spack.traverse.traverse_edges(
        specs, cover="edges", direction=direction, order="breadth", deptype=depflag
    ):
        spec_data = get_timings(edge.spec)
        if spec_data:
            for phase, time in spec_data.items():
                full_data = dag_data.get(phase, [])
                full_data.append(time)
                dag_data[phase] = full_data

    stats = {}
    for key, data in dag_data.items():
        stats[key] = {
            "mean": statistics.mean(data),
            "std": statistics.stdev(data),
            "quartiles": statistics.quantiles(data),
            "min": min(data),
            "max": max(data),
        }
    return stats


def analyze(parser, args):
    env = spack.cmd.require_active_env(cmd_name=command_name)
    if args.decay_points:
        specs = spack.cmd.parse_specs(args.decay_points)
        stats = compute_dag_stats(specs, direction="parents")
    else:
        specs = env.concrete_roots()
        stats = compute_dag_stats(specs)

    pretty_stats = json.dumps(stats, indent=4)
    sys.stdout.write(pretty_stats)


def add_command(parser, command_dict):
    subparser = parser.add_parser(
        command_name, description=description, help=description, aliases=aliases
    )
    setup_parser_args(subparser)
    command_dict[command_name] = analyze
    for alias in aliases:
        command_dict[alias] = analyze
