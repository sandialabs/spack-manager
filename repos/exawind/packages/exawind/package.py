from spack import *
#from spack.pkg.builtin.exawind import Exawind as bExawind
import os


class Exawind(CMakePackage, CudaPackage):
    """Multi-application driver for Exawind project."""

    homepage = "https://github.com/Exawind/exawind-driver"
    git = "https://github.com/Exawind/exawind-driver.git"

    maintainers = ['jrood-nrel']

    tags = ['ecp', 'ecp-apps']

    version('master', branch='main')
    variant('asan', default=False,
            description='turn on address sanitizer')

    depends_on('ninja', type='build')
    generator = 'Ninja'

    variant('openfast', default=False,
            description='Enable OpenFAST integration')
    variant('hypre', default=True,
            description='Enable hypre solver')

    for arch in CudaPackage.cuda_arch_values:
        depends_on('nalu-wind+cuda cuda_arch=%s' % arch, when='+cuda cuda_arch=%s' % arch)
        depends_on('amr-wind+cuda cuda_arch=%s' % arch, when='+cuda cuda_arch=%s' % arch)
        depends_on('trilinos+cuda cuda_arch=%s' % arch, when='+cuda cuda_arch=%s' % arch)

    depends_on('nalu-wind+tioga')
    depends_on('amr-wind+netcdf+mpi')
    depends_on('tioga+shared~nodegid')
    depends_on('yaml-cpp@0.6:')

    depends_on('nalu-wind+openfast', when='+openfast')
    depends_on('amr-wind+openfast', when='+openfast')
    depends_on('openfast+cxx+shared@2.6.0', when='+openfast')
    depends_on('nalu-wind+hypre', when='+hypre')
    depends_on('amr-wind+hypre', when='+hypre')

    def cmake_args(self):
        spec = self.spec

        args = super(Exawind, self).cmake_args()
        define = CMakePackage.define

        if 'dev_path' in spec:
            args.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if spec['mpi'].name == 'openmpi':
            args.append(define('MPIEXEC_PREFLAGS','--oversubscribe'))
        args.append(define('MPI_ROOT', spec['mpi'].prefix))

        return args

    def setup_build_environment(self, env):
        if '+asan' in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}".format(join_path(self.package_dir, 'sup.asan')))

    @run_after('cmake')
    def copy_compile_commands(self):
        if 'dev_path' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)

    @run_before('cmake')
    def add_submodules(self):
        git = which('git')
        git('submodule', 'update', '--init', '--recursive')
