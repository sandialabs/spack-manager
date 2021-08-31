from spack import *
from spack.pkg.builtin.exawind import Exawind as bExawind
import os


class Exawind(bExawind, CudaPackage):
    variant('asan', default=False,
            description='turn on address sanitizer')
    variant('openfast', default=False,
             description='Enable OpenFAST integration')

    depends_on('ninja', type='build')
    generator = 'Ninja'

    for arch in CudaPackage.cuda_arch_values:
        depends_on('nalu-wind+cuda cuda_arch=%s' % arch, when='+cuda cuda_arch=%s' % arch)
        depends_on('amr-wind+cuda cuda_arch=%s' % arch, when='+cuda cuda_arch=%s' % arch)
        depends_on('trilinos+cuda cuda_arch=%s' % arch, when='+cuda cuda_arch=%s' % arch)

    depends_on('nalu-wind+openfast', when='+openfast')
    depends_on('amr-wind+openfast', when='+openfast')
    depends_on('openfast+cxx+shared@2.6.0', when='+openfast')

    def cmake_args(self):
        spec = self.spec

        args = super(Exawind, self).cmake_args()

        if 'dev_path' in spec:
            args.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if spec['mpi'].name == 'openmpi':
            args.append(define('MPIEXEC_PREFLAGS','--oversubscribe'))

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
