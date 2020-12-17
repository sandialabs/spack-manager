#!/usr/bin/env spack-python
import pathlib
import sys
import os
import socket

script_loc = os.path.join(os.environ['SPACK_MANAGER'],'scripts')
sys.path.append(script_loc)

from spec_deploy import SpecEnvDeploy

hostname = socket.gethostname()

env_name = None
spec = None

if 'skybridge' in hostname:
    env_name = 'skybridge-nightly'
    spec = 'nalu-wind-nightly+hypre+tioga+openfast'
elif 'ascicgpu' in hostname:
    env_name = 'ascicgpu-nightly'
    spec = 'nalu-wind-nightly+hypre+tioga+openfast+cuda cuda_arch=70 ^cuda@9.2.148%gcc@7.2.0 ^openmpi@4.0.2'
else:
    raise Exception("Nightly test not supported for this platform yet")

SpecEnvDeploy(env_name, spec)
