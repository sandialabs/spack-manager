# Makefile to bootstrap compilers/mpi etc from scratch 
# Includes an intermeidate compiler to build more advanced compilers since the system compiler could be too old
#
export SPACK_USER_CONFIG_PATH=$(CURDIR)/.spack
export SPACK_USER_CACHE_PATH=$(CURDIR)/.spack
external_packages = perl m4 autoconf automake libtool gawk ncurses openssl openssh

.SUFFIXES:

.PHONY: all clean


all: packages/generated/env

clean:
	rm -rf bootstrap/
	rm -rf compilers/
	rm -rf packages/

## intermediate compiler (start with system compiler)
bootstrap/spack.yaml:
				mkdir -p bootstrap
				cp $(CURDIR)/bootstrap.yaml bootstrap/spack.yaml

bootstrap/compilers.yaml:
				SPACK_USER_CONFIG_PATH=bootstrap spack compiler find --scope=user

bootstrap/config.yaml:
				SPACK_USER_CONFIG_PATH=bootstrap spack config --scope=user add config:install_tree:root:$(CURDIR)/bootstrap_store

bootstrap/packages.yaml:
				SPACK_USER_CONFIG_PATH=bootstrap spack external find --scope=user $(external_packages)

bootstrap/spack.lock: bootstrap/spack.yaml bootstrap/config.yaml bootstrap/packages.yaml bootstrap/compilers.yaml
				spack -e bootstrap concretize --force

bootstrap/spack.mk: bootstrap/spack.lock
				spack -e bootstrap env depfile --make-target-prefix bootstrap/generated -o $@

# production compilers (depends on intermediate compilers)
compilers/spack.yaml:
				mkdir -p compilers
				cp $(CURDIR)/production_compilers.yaml compilers/spack.yaml

compilers/compilers.yaml: bootstrap/generated/env
				SPACK_USER_CONFIG_PATH=compilers spack compiler find --scope=user $$(spack -e bootstrap find --format '{prefix}' gcc)

compilers/config.yaml: 
				SPACK_USER_CONFIG_PATH=compilers spack config --scope=user add config:install_tree:root:$(CURDIR)/compilers_store

compilers/packages.yaml:
				SPACK_USER_CONFIG_PATH=compilers spack external find --scope=user $(external_packages)

compilers/spack.lock: compilers/spack.yaml compilers/config.yaml compilers/packages.yaml compilers/compilers.yaml
				spack -e compilers concretize --force

compilers/spack.mk: compilers/spack.lock
				spack -e compilers env depfile --make-target-prefix compilers/generated -o $@

# packages (depends on production compilers)
packages/spack.yaml:
				mkdir -p packages
				cp $(CURDIR)/production_packages.yaml packages/spack.yaml

packages/compilers.yaml: compilers/generated/env
				# use a view to find the intel compiler
				SPACK_USER_CONFIG_PATH=packages spack -e compilers compiler find --scope=user
				# selectively pull gcc and llvm to avoid system gcc
				SPACK_USER_CONFIG_PATH=packages spack compiler find --scope=user $$(spack -e compilers find --format '{prefix}' gcc llvm)

packages/config.yaml:
				SPACK_USER_CONFIG_PATH=packages spack config --scope=user add config:install_tree:root:$(CURDIR)/packages_store

packages/packages.yaml:
				SPACK_USER_CONFIG_PATH=packages spack external find --scope=user $(external_packages)

packages/spack.lock: packages/spack.yaml packages/config.yaml packages/packages.yaml packages/compilers.yaml
				spack python mixed_compiler_creator.py packages/compilers.yaml
				spack -e packages concretize --force

packages/spack.mk: packages/spack.lock
				spack -e packages env depfile --make-target-prefix packages/generated -o $@

ifeq (,$(filter clean,$(MAKECMDGOALS)))

include bootstrap/spack.mk

ifneq (,$(wildcard bootstrap/spack.mk))
include compilers/spack.mk
endif

ifneq (,$(wildcard compilers/spack.mk))
include packages/spack.mk
endif

endif
