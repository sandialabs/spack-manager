#!/usr/bin/env spack-python

"""
Build a nalu-wind package if none of the dependencies need to be installed
"""

from spack.spec import Spec
import spack.config

myscope = spack.config.ConfigScope('darwin', '/Users/psakiev/soft/spack-manager/configs/darwin/')
with spack.config.override(myscope):
  # setup spec
  s = Spec('nalu-wind').concretized()
  # echo spec to screen
  if(s.concrete):
      print(s.cshort_spec)
  else:
      print('Spec not concrete')
  # check if it has been installed
  deps_missing = False
  for dep in s.traverse():
      if dep != s:
            in_database = spack.store.db.query(dep, installed=True)  # the installed argument can be left off, that's the default
            if not in_database:
                print( 'NOT INSTALLED ' + dep.cshort_spec)
                deps_missing = True
  if deps_missing:
      exit()
  # build and install
  s.package.do_install()
  # create a view and hardlink
