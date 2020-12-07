"""
Courtesy of Greg Becker
"""
#!/usr/bin/env spack-python
import spack.config
import spack.util.spack_yaml as syaml
import sys
import llnl.util.tty as tty
import shutil
# Get a function to update the format
update_fn = spack.config.ensure_latest_format_fn(sys.argv[1])
cfg_file = sys.argv[2]
with open(cfg_file) as f:
    raw_data = syaml.load_config(f) or {}
    data = raw_data.pop(args.section, {})
update_fn(data)
# Make a backup copy and rewrite the file
bkp_file = cfg_file + '.bkp'
shutil.copy(cfg_file, bkp_file)
write_data = {section: data}
with open(cfg_file, 'w') as f:
    syaml.dump_config(write_data, stream=f, default_flow_style=False)
msg = 'File "{0}" updated [backup={1}]'
tty.msg(msg.format(cfg_file, bkp_file))
