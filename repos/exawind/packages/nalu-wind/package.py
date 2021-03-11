from spack import *
from spack.pkg.builtin.nalu_wind import NaluWind as bNaluWind
from spack.pkg.builtin.kokkos import Kokkos
import os
from shutil import copyfile

class NaluWind(bNaluWind):
    variant('asan', default=False,
            description='turn on address sanitizer')
    variant('compile_commands', default=False,
            description='generate compile_commands.json and copy to source dir')
    variant('tests', default=False,
            description='turn on tests')

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(NaluWind, self).cmake_args()

        if '+compile_commands' in spec:
            options.append(define('CMAKE_EXPORT_COMPILE_COMMANDS',True))

        if '+asan' in spec:
            cxx_flags+=' -fsanitize=address -fno-sanitize-address-use-after-scope'

        if '+tests' in spec:
            options.append(define('ENABLE_TESTS', True))

        return options

    @run_after('cmake')
    def copy_compile_commands(self):
        if '+compile_commands' in self.spec:
            target = os.path.join(self.stage.source_path, "compile_commands.json")
            source = os.path.join(self.build_directory, "compile_commands.json")
            copyfile(source, target)
