from spack import *
from spack.pkg.builtin.nalu_wind import NaluWind as bNaluWind
from spack.pkg.builtin.kokkos import Kokkos
import os
from shutil import copyfile

class NaluWind(bNaluWind):
    version('master', branch='master', submodules=True)
    variant('asan', default=False,
            description='turn on address sanitizer')
    depends_on('ninja', type='build')
    generator = 'Ninja'

    def setup_build_environment(self, env):
        if '+asan' in self.spec:
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer -fsanitize-blacklist={0}".format(join_path(self.package_dir, 'sup.asan')))

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(NaluWind, self).cmake_args()

        if 'dev_path' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))
            options.append(define('ENABLE_TESTS', True))

        if spec['mpi'].name == 'openmpi':
            options.append(define('MPIEXEC_PREFLAGS','--oversubscribe'))

        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        if 'dev_path' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
