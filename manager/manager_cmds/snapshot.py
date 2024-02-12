# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
import os

from environment_utils import SpackManagerEnvironmentManifest
from manager_cmds.create_env import create_env
from manager_cmds.pin import pin_env
from manager_utils import path_extension

import spack.cmd.install
import spack.environment as ev
import spack.main
import spack.util.spack_yaml as syaml

install = spack.main.SpackCommand("install")


class create_args:
    """
    class to mock out parsing for create-env
    """

    def __init__(self, name, use_machine_name, specs):
        self.extension = path_extension(name, use_machine_name)
        self.the_specs = specs

    @property
    def name(self):
        return None

    @property
    def yaml(self):
        # TODO the module root isn't getting renamed based off args.name like it should
        return os.path.join(os.environ["SPACK_MANAGER"], "env-templates", "snapshot.yaml")

    @property
    def spec(self):
        return self.the_specs

    @property
    def local_source(self):
        return True

    @property
    def machine(self):
        return None

    @property
    def directory(self):
        return os.path.join(os.environ["SPACK_MANAGER"], self.extension)


class pin_args:
    """
    class to mock out parsing pin args so we can use the functions
    """

    def __init_(self):
        pass

    @property
    def all(self):
        return True

    @property
    def dependencies(self):
        return None

    @property
    def roots(self):
        return None

    @property
    def fresh(self):
        return None


def create_snapshots(parser, args):
    """
    Command to create the snapshot environment
    if we use latest git hashes then this will have to concretize twice
    first to create concrete specs so we can loop over the DAG and replace
    versions with git hashes
    and then to concretize after the specs get updated
    """

    # setup parser args for embedded commands
    cargs = create_args(args.name, args.use_machine_name, args.specs)
    pargs = pin_args()
    module_root = os.path.join(os.environ["SPACK_MANAGER"], "modules", cargs.extension)

    env_path = create_env(None, cargs)

    # update module path based on the name given
    manifest = SpackManagerEnvironmentManifest(env_path)
    manifest.set_config_value("modules", "default", {"roots": {"lmod": module_root}})
    # add core compilers
    includes = os.path.join(env_path, "include.yaml")
    if os.path.isfile(includes):
        core_compilers = []
        with open(includes, "r") as ifile:
            iyaml = syaml.load_config(ifile)
            if "compilers" in iyaml:
                for compiler in iyaml["compilers"]:
                    print(compiler)
                    core_compilers.append(compiler["compiler"]["spec"])
        manifest.set_config_value(
            "modules", "default", {"lmod": {"core_compilers": core_compilers}}
        )
    manifest.flush()

    env = ev.Environment(env_path)
    ev.activate(env)

    pin_env(None, pargs)

    if args.install:
        install()

    return env_path


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        "snapshot",
        help="create a timestamped snapshot environment for registered machines.  The install tree"
        " will be held in the environment location to preserve the builds over time and the "
        "installed packages will not be visible to the rest of the spack database outside the "
        "environment.",
    )
    sub_parser.add_argument(
        "--regular_versions",
        "-r",
        action="store_true",
        required=False,
        help="don't replace branch version with latest git hashes as verions",
    )
    sub_parser.add_argument(
        "--name",
        "-n",
        required=False,
        help="name the environment something other than the " "date",
    )
    sub_parser.add_argument(
        "--use_machine_name",
        "-m",
        action="store_true",
        help="use machine name in the snapshot path " "instead of computed architecture",
    )
    sub_parser.add_argument(
        "-s", "--specs", required=True, default=[], nargs="+", help="Specs to create snapshots for"
    )
    sub_parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        required=False,
        help="install the environment as part of this command rather than as a separate step.  "
        "Depfile installs are generally prefered over using this option",
    )
    command_dict["snapshot"] = create_snapshots
