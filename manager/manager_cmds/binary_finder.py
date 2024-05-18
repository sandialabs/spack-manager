# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.


import spack.cmd
import spack.binary_distribution as bindist

command_name = "binary-finder"
description = "check upstreams and binary caches for hits on a concretized environment"
aliases = ["bf"]


def setup_parser_args(subparser):
    subparser.add_argument(
        "--source",
        "-s",
        choices=["cache", "upstream", "both"],
        default="both",
        help="source where hits can come from",
    )
    subparser.add_argument(
        "--output",
        "-o",
        choices=["miss", "hit", "both"],
        default="miss",
        help="what type of cache queries are output",
    )


def binary_finder(parser, args):
    env = spack.cmd.require_active_env(cmd_name=command_name)
    hashes = env.all_hashes()
    n = len(hashes)
    # TODO clean misc cache

    print(f"Querying buildcache for {n} specs")
    bindist.BINARY_INDEX.regenerate_spec_cache()
    misses = []
    hits = []

    def cache_hit(h):
        return bool(bindist.BINARY_INDEX.find_by_hash(h)) 

    def upstream_hit(spec):
        return spec.installed_upstream

    for i, h in enumerate(hashes):
        # serial loop over all the hashes, would be commented out if using a Pool
        spec = env.get_one_by_hash(h)

        hit = False
        if args.source != "upstream":
            hit = hit or cache_hit(h)
        if args.source != "cache":
            hit = hit or upstream_hit(spec)

        if hit:
            hits.append((h, spec))
        else:
            misses.append((h, spec))

        # status printer probably not good for spack due to excess output
        #j = i + 1
        #time.sleep(0.01)
        #if j != n:
        #    print(f"\r-- {j}/{n}", end="\r")
        #else:
        #    print(f"\r-- {j}/{n}", end="\n")

    if args.output == "miss" or args.output == "both":
        print("----------------------------------------")
        print("Cache Miss Legend")
        print("[E]: External")
        print("[D]: Develop Spec")
        print("[-]: True Miss")
        print("----------------------------------------")
        print("\n----------------------------------------")
        print("The following {} specs missed in the cache:".format(len(misses)))
        print("----------------------------------------")

        def miss_reason(spec):
            template = "[{}]"
            if env.is_develop(spec):
                return template.format("D")
            elif spec.external:
                return template.format("E")
            elif spec.installed_upstream:
                return template.format("U")
            else:
                return template.format("-")

        for miss in misses:
            h, s = miss
            mark = miss_reason(s)
            spec_name = s.name
            print(f"/{h}: {mark} {s.name}")

    if args.output == "hit" or args.output == "both":
        print("\n----------------------------------------")
        print("The following {} specs hit in the cache:".format(len(hits)))
        print("----------------------------------------")
        for hit in hits:
            h, s = hit
            spec_name = s.name
            print(f"/{h}: [+] {s.name}")

    print("\n----------------------------------------")
    print("Summary: Hits ({}) Misses ({})".format(len(hits), len(misses)))
    print("----------------------------------------")


def add_command(parser, command_dict):
    subparser = parser.add_parser(
        command_name,
        description=description,
        help=description,
        aliases=aliases
    )
    setup_parser_args(subparser)
    command_dict[command_name] = binary_finder
    for alias in aliases:
        command_dict[alias] = binary_finder
