from spack import *
from spack.pkg.pending.exawind import Exawind as bExawind
import os


class ExawindDeveloper(bExawind):
    version('master', branch='main', submodules=True)

    variant('asan', default=False,
            description='Turn on address sanitizer')
    variant('compile_commands', default=True,
            description='Tenerate compile_commands.json and copy to source dir')

    def setup_build_environment(self, env):
        if '+asan' in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}".format(join_path(self.package_dir, 'sup.asan')))

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(ExawindDeveloper, self).cmake_args()

        if '+compile_commands' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if spec['mpi'].name == 'openmpi':
            options.append(define('MPIEXEC_PREFLAGS','--oversubscribe'))

        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        if '+compile_commands' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
