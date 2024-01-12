# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import llnl.util.tty as tty

import spack
import spack.config
import spack.detection
import spack.environment as ev
import spack.util.spack_yaml as syaml
from spack.detection.common import _pkg_config_dict
from spack.extensions.manager.environment_utils import SpackManagerEnvironmentManifest
from spack.extensions.manager.manager_utils import pruned_spec_string
from spack.spec import Spec


def include_entry_exists(env, name):
    manifest = SpackManagerEnvironmentManifest(env.manifest.manifest_dir)
    includes = manifest.pristine_configuration.get("include", [])
    for entry in includes:
        if entry == name:
            return True
    return False


def add_include_entry(env, inc, prepend=True):
    manifest = SpackManagerEnvironmentManifest(env.manifest.manifest_dir)
    if prepend:
        manifest.prepend_includes(inc)
    else:
        manifest.append_includes(inc)
    manifest.flush()


def create_external_detected_spec(env, spec):
    view = _get_first_view_containing_spec(env, spec)
    pruned_spec = pruned_spec_string(spec)
    prefix = view.get_projection_for_spec(spec)
    if not os.path.isdir(prefix):
        return None
    # attempt to return a valid spec using the current spack instance
    try:
        return spack.detection.DetectedPackage(Spec.from_detection(pruned_spec), prefix)
    except spack.variant.UnknownVariantError:
        # if it is an old spec then a variant could have changed so we just create a spec from the
        # pruned_spec string
        return spack.detection.DetectedPackage(Spec(pruned_spec), prefix)


def assemble_dict_of_detected_externals(env, black_list, white_list):
    external_spec_dict = {}
    active_env = ev.active_environment()

    def update_dictionary(env, spec):
        ext_spec = create_external_detected_spec(env, spec)
        if ext_spec:
            if spec.name in external_spec_dict:
                external_spec_dict[spec.name].append(ext_spec)
            else:
                external_spec_dict[spec.name] = [ext_spec]
        else:
            return

    for spec in env.all_specs():
        if spec.external:
            continue
        if black_list:
            if spec.name not in black_list:
                update_dictionary(env, spec)
        elif white_list:
            if spec.name in white_list:
                update_dictionary(env, spec)
        else:
            if not active_env.is_develop(spec):
                update_dictionary(env, spec)
    return external_spec_dict


def create_yaml_from_detected_externals(ext_dict):
    formatted_dict = {}
    for name, entries in ext_dict.items():
        config = _pkg_config_dict(entries)
        config["buildable"] = False
        formatted_dict[name] = config

    return syaml.syaml_dict({"packages": formatted_dict})


def _get_first_view_containing_spec(env, spec):
    for view in env.views.values():
        if view.__contains__(spec):
            return view
    return None


def external(parser, args):
    env = ev.active_environment()
    if not env:
        tty.die("spack manager external requires an active environment")

    # check that directory of ext view exists
    if not ev.is_env_dir(args.path):
        tty.die(
            "External path must point to a spack environment with a view. "
            "Auto detection of the latest dated snapshot can be achived"
            " with the '--latest' flag."
        )

    snap_env = ev.Environment(args.path)
    snap_env.check_views()

    if not snap_env.views:
        tty.die("Environments used to create externals must have at least 1" " associated view")
    # copy the file and overwrite any that may exist (or merge?)
    inc_name_abs = os.path.abspath(os.path.join(env.path, args.name))

    try:
        detected = assemble_dict_of_detected_externals(snap_env, args.exclude, args.include)
        src = create_yaml_from_detected_externals(detected)
    except ev.SpackEnvironmentError as e:
        tty.die(e.long_message)

    if include_entry_exists(env, args.name):
        if args.merge:
            # merge the existing includes with the new one
            # giving precedent to the new data coming in
            dest = spack.config.read_config_file(
                inc_name_abs, spack.config.section_schemas["packages"]
            )
            combined = spack.config.merge_yaml(src, dest)
            final = combined
        else:
            final = src
    else:
        add_include_entry(env, args.name)
        final = src

    with open(inc_name_abs, "w") as fout:
        syaml.dump_config(final, stream=fout, default_flow_style=False)

    env.write()


def add_command(parser, command_dict):
    ext = parser.add_parser(
        "external",
        help="tools for configuring precompiled" " binaries",
        conflict_handler="resolve",
    )

    ext.add_argument(
        "-n",
        "--name",
        required=False,
        help="name the new include file for the " "externals with this name",
    )
    ext.add_argument(
        "-m",
        "--merge",
        required=False,
        action="store_true",
        help="merge existing yaml files " "together",
    )

    select = ext.add_mutually_exclusive_group()

    select.add_argument(
        "-i",
        "--include",
        nargs="*",
        required=False,
        help="(not implemeted) specs that should " "be added (omit all others)",
    )
    select.add_argument(
        "-e",
        "--exclude",
        nargs="*",
        required=False,
        help="(not implemented) specs that should " "be omitted (add all others)",
    )
    ext.add_argument("path", nargs="?", help="The location of the external install " "directory")
    ext.set_defaults(merge=False, name="externals.yaml")

    command_dict["external"] = external
