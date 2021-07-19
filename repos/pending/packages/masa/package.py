from spack.pkg.builtin.masa import Masa as bMasa

class Masa(bMasa):
    # Solve c++11 errors and "implicit declaration of function is invalid in C99 error" with apple-clang
    def setup_build_environment(self, env):
        # Unfortunately can't use this because MASA overwrites it
        #env.set('CXXFLAGS', self.compiler.cxx11_flag)
        env.set('CXX', "{0} {1}".format(self.compiler.cxx, self.compiler.cxx11_flag))
        if self.spec.satisfies('%apple-clang'):
            env.set('CFLAGS', '-Wno-implicit-function-declaration')
