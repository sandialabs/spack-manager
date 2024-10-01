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
from typing import List, Optional, Set, TextIO, Tuple

import spack.cmd
import spack.deptypes as dt
import spack.traverse as traverse
from spack.graph import DotGraphBuilder

command_name = "analyze"
description = "tooling for analyzing statistics of the DAG"
aliases = []


class OmmitSpecsVisitor(traverse.BaseVisitor):
    """A visitor that clips the graph upon satisfied specs"""

    def __init__(self, clip_specs):
        super().__init__()
        self.clip_specs = clip_specs
        self.accepted = []

    def accept(self, node):
        key = node.edge.spec
        test = not any(key.satisfies(p) for p in self.clip_specs)
        if test:
            self.accepted.append(node)
        return test


def setup_parser_args(subparser):
    subparser.add_argument(
        "--trim-packages", nargs="+", default=[], help="clip the graph at these packages"
    )
    subparser.add_argument(
        "--stats", action="store_true", help="display stats for graph build/install"
    )
    subparser.add_argument(
        "--graph", action="store_true", help="generate a dot file of the graph requested"
    )
    subparser.add_argument(
        "--scale-nodes",
        action="store_true",
        help="scale graph nodes relative to the mean install time",
    )
    subparser.add_argument(
        "--heatmap", action="store_true", help="color graph nodes based on the time to build"
    )


def traverse_nodes_with_ommissions(specs, ommissions):
    visitor = OmmitSpecsVisitor(ommissions)
    traverse.traverse_breadth_first_with_visitor(specs, traverse.CoverNodesVisitor(visitor))
    return visitor.accepted


def get_timings(spec):
    if spec.installed:
        timing_files = spec.package.times_log_path
        if os.path.isfile(timing_files):
            with open(timing_files, "r") as f:
                spec_data = json.load(f)
                # extract phases
                output = {"total": 0.0}
                for phase in spec_data["phases"]:
                    output[phase["name"]] = phase["seconds"]
                    output["total"] += phase["seconds"]
                return output
    return None


def compute_dag_stats(specs, trim_specs=[], depflag=dt.ALL):
    dag_data = {}
    nodes = traverse_nodes_with_ommissions(specs, trim_specs)
    for node in nodes:
        spec_data = get_timings(node.edge.spec)
        if spec_data:
            for phase, time in spec_data.items():
                full_data = dag_data.get(phase, [])
                full_data.append(time)
                dag_data[phase] = full_data

    stats = {}
    for key, data in dag_data.items():
        stats[key] = {
            "mean": statistics.mean(data),
            "stddev": statistics.stdev(data) if len(data) > 1 else 0,
            "quartiles": statistics.quantiles(data) if len(data) > 1 else [0, 0, 0],
            "min": min(data),
            "max": max(data),
            "sum": sum(data),
        }
    return stats


class StatsGraphBuilder(DotGraphBuilder):
    def __init__(self, stats, to_color=False, to_scale=False):
        super().__init__()
        self.dag_stats = stats
        self.to_color = to_color
        self.to_scale = to_scale

    def _get_scaling_factor(self, mean, time):
        return time / mean

    def _get_properties(self, spec):
        timings = get_timings(spec)
        if timings:
            total = timings["total"]
            scaling = self._get_scaling_factor(self.dag_stats["mean"], total)
            if total < self.dag_stats["std"]:
                return "lightblue", scaling
            elif total <= self.dag_stats["mean"] + self.dag_stats["std"]:
                return "green", scaling
            elif total <= self.dag_stats["mean"] + 2.0 * self.dag_stats["std"]:
                return "yellow", scaling
            else:
                return "red", scaling
        return "dodgerblue", 1.0

    def node_entry(self, node):
        color_compute, scale_factor = self._get_properties(node)
        x = 3.0
        y = 1.0
        fontsize = 48
        if self.to_scale:
            x *= scale_factor
            y *= scale_factor
            fontsize *= scale_factor
        scale_str = f"width={x} height={y} fixedsize=true fontsize={fontsize}"
        color_str = f'fillcolor="{color_compute if self.to_color else"lightblue"}"'

        return (node.dag_hash(), f'[label="{node.format("{name}")}", {color_str}, {scale_str}]')

    def edge_entry(self, edge):
        return (edge.parent.dag_hash(), edge.spec.dag_hash(), None)


def graph_dot(specs, builder, trim_packages=[], depflag=dt.ALL, out=None):
    """DOT graph of the concrete specs passed as input.

    Args:
        specs: specs to be represented
        builder: builder to use to render the graph
        depflag: dependency types to consider
        out: optional output stream. If None sys.stdout is used
    """
    if not specs:
        raise ValueError("Must provide specs to graph_dot")

    if out is None:
        out = sys.stdout

    builder = builder or SimpleDAG()
    for edge in spack.traverse.traverse_edges(
        specs, cover="edges", order="breadth", deptype=depflag
    ):
        builder.visit(edge)

    out.write(builder.render())


def analyze(parser, args):
    env = spack.cmd.require_active_env(cmd_name=command_name)
    specs = env.concrete_roots()
    stats = compute_dag_stats(specs, args.trim_packages)

    if args.stats:
        pretty_stats = json.dumps(stats, indent=4)
        sys.stdout.write(pretty_stats)

    if args.graph:
        builder = StatsGraphBuilder(stats["total"], args.heatmap, args.scale_nodes)
        graph_dot(specs, args.trim_packages, builder=builder)


def add_command(parser, command_dict):
    subparser = parser.add_parser(
        command_name, description=description, help=description, aliases=aliases
    )
    setup_parser_args(subparser)
    command_dict[command_name] = analyze
    for alias in aliases:
        command_dict[alias] = analyze
