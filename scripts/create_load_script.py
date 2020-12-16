#!/usr/bin/env spack-python
from spack.main import SpackCommand
import sys
import os

my_env = sys.argv[1]
loc = SpackCommand('location')
env = SpackCommand('env')

# check env
if my_env not in env('list'):
  print('Env not installed')
  exit()
# create load
env('activate', my_env)
#env('loads', '-r')
# read load into buffer
lf_loc = os.path.join(loc('-e',my_env).strip('\n'), 'loads')
lf = open(lf_loc, 'r')
data = lf.read()
lf.close()
# write buffer with prepen
final_loc = os.path.join(os.environ['SPACK_MANAGER'],'loads',my_env)
final = open(final_loc, 'w')
final.write('. {spr}/share/spack/setup_env.sh\n'.format(spr=os.environ['SPACK_ROOT'])+data)
final.close()
os.chmod(final_loc, 0o755)