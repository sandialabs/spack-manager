# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file

import spack
import spack.extensions as ext


def location(verbose=False):
    if spack.spack_version_info[0:3] < (0, 22, 0):
        path = ext.path_for_extension("manager", ext.get_extension_paths())
    else:
        path = ext.path_for_extension("manager", paths=ext.get_extension_paths())
    if verbose:
        print(path)
    return path


def location_wrapper(parser, args):
    location(True)


def add_command(parser, command_dict):
    parser.add_parser("location", help="location of the spack-manager extension")
    command_dict["location"] = location_wrapper
