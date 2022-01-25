from spack import *
#from spack.pkg.builtin.exawind import Exawind as bExawind
from shutil import copyfile
import os


class Exawind(CMakePackage, CudaPackage, ROCmPackage):
    """Multi-application driver for Exawind project."""

    homepage = "https://github.com/Exawind/exawind-driver"
    git = "https://github.com/Exawind/exawind-driver.git"

    maintainers = ['jrood-nrel']

    tags = ['ecp', 'ecp-apps']

    # Testing is currently always enabled, but should be optional in the future
    # to avoid cloning the mesh submodule
    version('master', branch='main', submodules=True)

    variant('asan', default=False,
            description='turn on address sanitizer')
    variant('openfast', default=False,
            description='Enable OpenFAST integration')
    variant('hypre', default=True,
            description='Enable hypre solver')
    variant('amr_wind_gpu', default=False,
            description='Enable AMR-Wind on the GPU')
    variant('nalu_wind_gpu', default=False,
            description='Enable Nalu-Wind on the GPU')

    conflicts('+amr_wind_gpu', when='~cuda~rocm')
    conflicts('+nalu_wind_gpu', when='~cuda~rocm')
    conflicts('+amr_wind_gpu~nalu_wind_gpu', when='^amr-wind+hypre')

    for arch in CudaPackage.cuda_arch_values:
        depends_on('amr-wind+cuda cuda_arch=%s' % arch, when='+amr_wind_gpu+cuda cuda_arch=%s' % arch)
        depends_on('nalu-wind+cuda cuda_arch=%s' % arch, when='+nalu_wind_gpu+cuda cuda_arch=%s' % arch)
        depends_on('trilinos+cuda cuda_arch=%s' % arch, when='+nalu_wind_gpu+cuda cuda_arch=%s' % arch)

    for arch in ROCmPackage.amdgpu_targets:
        depends_on('amr-wind+rocm amdgpu_target=%s' % arch, when='+amr_wind_gpu+rocm amdgpu_target=%s' % arch)

    depends_on('nalu-wind+tioga')
    depends_on('amr-wind+netcdf+mpi')
    depends_on('tioga+shared~nodegid')
    depends_on('yaml-cpp@0.6:')
    depends_on('nalu-wind+openfast', when='+openfast')
    depends_on('amr-wind+openfast', when='+openfast')
    depends_on('openfast+cxx+shared@2.6.0', when='+openfast')
    depends_on('nalu-wind+hypre', when='+hypre')
    depends_on('amr-wind+hypre', when='+hypre')
    # not required but added so these get picked up as a
    # direct dependency when creating snapshots
    depends_on('trilinos')
    depends_on('cmake')
    depends_on('hypre', when='+hypre')

    def cmake_args(self):
        spec = self.spec

        args = super(Exawind, self).cmake_args()
        define = CMakePackage.define

        if spec.satisfies('dev_path=*'):
            args.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if spec['mpi'].name == 'openmpi':
            args.append(define('MPIEXEC_PREFLAGS','--oversubscribe'))
        args.append(define('MPI_ROOT', spec['mpi'].prefix))

        if spec.satisfies('+cuda'):
            args.append(define('EXAWIND_ENABLE_CUDA', True))
            args.append(define('CUDAToolkit_ROOT', self.spec['cuda'].prefix))

        if spec.satisfies('+rocm'):
            args.append(define('EXAWIND_ENABLE_ROCM', True))
            args.append('-DCMAKE_CXX_COMPILER={0}'.format(self.spec['hip'].hipcc))

        return args

    def setup_build_environment(self, env):
        if '+asan' in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}".format(join_path(self.package_dir, 'sup.asan')))

    @run_after('cmake')
    def copy_compile_commands(self):
        source = os.path.join(self.build_directory, "compile_commands.json")
        if self.spec.satisfies('dev_path=*') and os.path.isfile(source):
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            copyfile(source, target)
