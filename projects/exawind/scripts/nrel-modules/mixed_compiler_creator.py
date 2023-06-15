#  Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.
import sys

import spack.util.spack_yaml as syaml

file = sys.argv[1]
with open(file, "r") as fyaml:
    yaml = syaml.load_config(fyaml)

# needs to be compilers.yaml
assert "compilers" in yaml
# need at least two compilers
assert len(yaml["compilers"]) > 1


needs_compiler = {}
first_has_compiler = {"cc": None, "cxx": None, "f77": None, "fc": None}

# populate first positive hit
for comp in yaml["compilers"]:
    for key, value in comp["compiler"]["paths"].items():
        if not first_has_compiler[key] and (value and value != "null"):
            first_has_compiler[key] = value

# fill in missing values
for comp in yaml["compilers"]:
    for key, value in comp["compiler"]["paths"].items():
        if not value or value == "null":
            comp["compiler"]["paths"][key] = first_has_compiler[key]

with open(file, "w") as fyaml:
    syaml.dump_config(yaml, stream=fyaml, default_flow_style=False)
