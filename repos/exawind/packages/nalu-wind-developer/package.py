from spack import *
from spack.pkg.exawind.nalu_wind import NaluWind as bNaluWind
from spack.pkg.builtin.kokkos import Kokkos
import os
from shutil import copyfile

class NaluWindDeveloper(bNaluWind):
    variant('asan', default=False,
            description='turn on address sanitizer')
    variant('compile_commands', default=False,
            description='generate compile_commands.json and copy to source dir')
    variant('tests', default=False,
            description='turn on tests')

    def setup_build_environment(self, env):
        if '+asan' in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}".format(join_path(self.package_dir, 'sup.asan')))

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(NaluWindDeveloper, self).cmake_args()

        if '+compile_commands' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if '+tests' in spec:
            options.append(define('ENABLE_TESTS', True))

        if spec['mpi'].name == 'openmpi':
            options.append(define('MPIEXEC_PREFLAGS','--oversubscribe'))

        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        if '+compile_commands' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
