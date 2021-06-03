#!/usr/bin/env spack-python
"""
A script to prepend a loads file with the command to
source spack so users can just source the loads script
without first sourcing setup-env.sh
"""
from spack.main import SpackCommand
import spack.environment as ev
import sys
import os

def CreateUserLoads(my_env):
    loc = SpackCommand('location')
    env = SpackCommand('env')

    # check env
    if not ev.exists(my_env):
        raise Exception('Env not installed')
    # create load
    with ev.read(my_env):
         env('loads', '-r')
    # read load into buffer
    lf_loc = os.path.join(loc('-e',my_env).strip('\n'), 'loads')
    lf = open(lf_loc, 'r')
    data = lf.read()
    lf.close()
    # write buffer with prepen
    final_loc = os.path.join(os.environ['SPACK_MANAGER'],'loads',my_env)
    final = open(final_loc, 'w')
    final.write('. {spr}/share/spack/setup-env.sh\n'.format(spr=os.environ['SPACK_ROOT'])+data)
    final.close()
    os.chmod(final_loc, 0o755)

if __name__ == '__main__':
    CreateUserLoads(sys.argv[1])
