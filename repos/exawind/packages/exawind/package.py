from spack import *
import os


class Exawind(CMakePackage):
    """Multi-application driver for Exawind project."""

    homepage = "https://github.com/Exawind/exawind-driver"
    git = "https://github.com/Exawind/exawind-driver.git"

    maintainers = ['jrood-nrel']

    tags = ['ecp', 'ecp-apps']

    version('master', branch='main')

    variant('asan', default=False,
            description='turn on address sanitizer')

    depends_on('trilinos+stk')
    depends_on('tioga+shared~nodegid')
    depends_on('nalu-wind+hypre+openfast+tioga+wind-utils')
    depends_on('amr-wind+hypre+mpi+netcdf+openfast')
    depends_on('openfast+cxx+shared@2.6.0')
    depends_on('yaml-cpp@0.6:')

    def cmake_args(self):
        spec = self.spec

        args = [
            self.define('Trilinos_DIR', spec['trilinos'].prefix),
            self.define('TIOGA_DIR', spec['tioga'].prefix),
            self.define('Nalu-Wind_DIR', spec['nalu-wind'].prefix),
            self.define('AMR-Wind_DIR', spec['amr-wind'].prefix),
            self.define('OpenFAST_DIR', spec['openfast'].prefix),
            self.define('YAML-CPP_DIR', spec['yaml-cpp'].prefix)
        ]
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
