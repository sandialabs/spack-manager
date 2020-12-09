#!/usr/bin/env spack-python
import spack.config
import spack.util.spack_yaml as syaml
import sys
import llnl.util.tty as tty
import shutil
import os

# Get a function to update the format
def config_updater(cfg_type, cfg_file):
    """
    Courtesy of Greg Becker
    """
    update_fn = spack.config.ensure_latest_format_fn(cfg_type)
    with open(cfg_file) as f:
        raw_data = syaml.load_config(f) or {}
        data = raw_data.pop(cfg_type, {})
    update_fn(data)
    # Make a backup copy and rewrite the file
    bkp_file = cfg_file + '.bkp'
    shutil.copy(cfg_file, bkp_file)
    write_data = {cfg_type: data}
    with open(cfg_file, 'w') as f:
        syaml.dump_config(write_data, stream=f, default_flow_style=False)
    msg = 'File "{0}" updated [backup={1}]'
    tty.msg(msg.format(cfg_file, bkp_file))

if __name__ == '__main__':
    myTypes = ['config', 'packages', 'compilers']
    myDir = sys.argv[1]
    ftemplate = os.path.join(myDir, '{tpe}.yaml')
    for typ in myTypes:
        resolved = ftemplate.format(tpe=typ)
        if os.path.isfile(resolved):
            config_updater(typ, resolved)

