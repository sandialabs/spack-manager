# Makefile to bootstrap compilers/mpi etc from scratch 
# Includes an intermeidate compiler to build more advanced compilers since the system compiler could be too old
#
export SPACK_USER_CONFIG_PATH=$(CURDIR)/.spack
export SPACK_USER_CACHE_PATH=$(CURDIR)/.spack

.SUFFIXES:

.PHONY: all clean

all: tpls/generated/env

clean:
	rm -rf icomp/spack.mk icomp/spack.lock icomp/compilers.yaml icomp/config.yaml icomp/packages.yaml icomp/generated icomp/.spack-env
	rm -rf pcomps/spack.mk pcomps/spack.lock pcomps/compilers.yaml pcomps/config.yaml pcomps/packages.yaml pcomps/generated pcomps/.spack-env
	rm -rf tpls/spack.mk tpls/spack.lock tpls/compilers.yaml tpls/config.yaml tpls/packages.yaml tpls/generated tpls/.spack-env

## intermediate compiler (start with system compiler)
icomp/compilers.yaml:
				SPACK_USER_CONFIG_PATH=icomp spack compiler find --scope=user

icomp/config.yaml:
				SPACK_USER_CONFIG_PATH=icomp spack config --scope=user add config:install_tree:root:$(CURDIR)/icomp_store

icomp/packages.yaml:
				SPACK_USER_CONFIG_PATH=icomp spack external find --scope=user perl m4 autoconf automake libtool gawk

icomp/spack.lock: icomp/spack.yaml icomp/config.yaml icomp/packages.yaml icomp/compilers.yaml
				spack -e icomp concretize --force

icomp/spack.mk: icomp/spack.lock
				spack -e icomp env depfile --make-target-prefix icomp/generated -o $@

# production compilers (depends on intermediate compilers)
pcomps/compilers.yaml: icomp/generated/env
				SPACK_USER_CONFIG_PATH=pcomps spack compiler find --scope=user $$(spack -e icomp find --format '{prefix}' gcc)

pcomps/config.yaml: 
				SPACK_USER_CONFIG_PATH=pcomps spack config --scope=user add config:install_tree:root:$(CURDIR)/pcomp_store

pcomps/packages.yaml:
				SPACK_USER_CONFIG_PATH=pcomps spack external find --scope=user perl m4 autoconf automake libtool gawk ncurses openssl

pcomps/spack.lock: pcomps/spack.yaml pcomps/config.yaml pcomps/packages.yaml pcomps/compilers.yaml
				spack -e pcomps concretize --force

pcomps/spack.mk: pcomps/spack.lock
				spack -e pcomps env depfile --make-target-prefix pcomps/generated -o $@

# tpls (depends on production compilers)
tpls/compilers.yaml: pcomps/generated/env
				SPACK_USER_CONFIG_PATH=tpls spack compiler find --scope=user $$(spack -e pcomps find --format '{prefix}' gcc llvm)

tpls/config.yaml:
				SPACK_USER_CONFIG_PATH=tpls spack config --scope=user add config:install_tree:root:$(CURDIR)/tpls_store

tpls/packages.yaml:
				SPACK_USER_CONFIG_PATH=tpls spack external find --scope=user perl m4 autoconf automake libtool gawk ncurses openssl openssh libxcrypt

tpls/spack.lock: tpls/spack.yaml tpls/config.yaml tpls/packages.yaml tpls/compilers.yaml
				spack python mixed_compiler_creator.py tpls/compilers.yaml
				spack -e tpls concretize --force

tpls/spack.mk: tpls/spack.lock
				spack -e tpls env depfile --make-target-prefix tpls/generated -o $@

ifeq (,$(filter clean,$(MAKECMDGOALS)))

include icomp/spack.mk

ifneq (,$(wildcard icomp/spack.mk))
include pcomps/spack.mk
endif

ifneq (,$(wildcard pcomps/spack.mk))
include tpls/spack.mk
endif

endif
