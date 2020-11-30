#!/usr/bin/env spack-python
from spack.spec import Spec
import spack.config
import sys
import os
sys.path.append(os.environ['SPACK_MANAGER']+r'/scripts')
from SpackConfigRunner import SpackConfigRunner

"""
Run nightly test of nalu-wind
"""
def RunNightlyTest():
    s = Spec('nalu-wind-nightly+openfast+hypre+tioga').concretized()
    if spack.store.db.query(s, installed=True):
        s.package.do_uninstall()
    s.package.do_install()

if __name__ == '__main__':
    print(sys.path)
    runner = SpackConfigRunner()
    runner(RunNightlyTest)
