# Makefile to bootstrap compilers/mpi etc from scratch 
# Includes an intermeidate compiler to build more advanced compilers since the system compiler could be too old

export SPACK_USER_CONFIG_PATH=$(CURDIR)/.spack
export SPACK_USER_CACHE_PATH=$(CURDIR)/.spack
unexport SPACK_DISABLE_LOCAL_CONFIG
#Ellis
INSTALLDIR = /data/ssd1/software/2020-11-28
#Rhodes
#INSTALLDIR = /opt/software/2020-11-28

.SUFFIXES:

.PHONY: all clean


all: packages/generated/modules

clean:
	rm -rf bootstrap/
	rm -rf compilers/
	rm -rf packages/

# Bootstrap packages
bootstrap/spack.yaml:
	mkdir -p bootstrap
	cp $(CURDIR)/bootstrap.yaml bootstrap/spack.yaml

bootstrap/compilers.yaml:
	SPACK_USER_CONFIG_PATH=bootstrap spack compiler find --scope=user

bootstrap/config.yaml:
	SPACK_USER_CONFIG_PATH=bootstrap spack config --scope=user add config:install_tree:root:$(INSTALLDIR)/opt/bootstrap
	SPACK_USER_CONFIG_PATH=bootstrap spack config --scope=user add modules:default:roots:tcl:$(INSTALLDIR)/modules/bootstrap

bootstrap/packages.yaml:
	touch bootstrap/packages.yaml
	#SPACK_USER_CONFIG_PATH=bootstrap spack external find --scope=user $(external_packages)

bootstrap/spack.lock: bootstrap/spack.yaml bootstrap/config.yaml bootstrap/packages.yaml bootstrap/compilers.yaml
	spack -e bootstrap concretize --force

bootstrap/spack.mk: bootstrap/spack.lock
	spack -e bootstrap env depfile --make-target-prefix bootstrap/generated -o $@

bootstrap/generated/modules: bootstrap/generated/env
	spack -e bootstrap module tcl refresh -y
	touch bootstrap/generated/modules

# Compilers
compilers/spack.yaml:
	mkdir -p compilers
	cp $(CURDIR)/production_compilers.yaml compilers/spack.yaml

compilers/compilers.yaml: bootstrap/generated/modules
	SPACK_USER_CONFIG_PATH=compilers spack compiler find --scope=user $$(spack -e bootstrap find --format '{prefix}' gcc)

compilers/config.yaml: 
	SPACK_USER_CONFIG_PATH=compilers spack config --scope=user add config:install_tree:root:$(INSTALLDIR)/opt/compilers
	SPACK_USER_CONFIG_PATH=compilers spack config --scope=user add modules:default:roots:tcl:$(INSTALLDIR)/modules/compilers

compilers/packages.yaml:
	touch compilers/packages.yaml
	#SPACK_USER_CONFIG_PATH=compilers spack external find --scope=user $(external_packages)

compilers/spack.lock: compilers/spack.yaml compilers/config.yaml compilers/packages.yaml compilers/compilers.yaml
	spack -e compilers concretize --force

compilers/spack.mk: compilers/spack.lock
	spack -e compilers env depfile --make-target-prefix compilers/generated -o $@

compilers/generated/modules: compilers/generated/env
	spack -e compilers module tcl refresh -y
	touch compilers/generated/modules

# Packages
packages/spack.yaml:
	mkdir -p packages
	cp $(CURDIR)/production_packages.yaml packages/spack.yaml

packages/compilers.yaml: compilers/generated/modules
	# selectively pull gcc and llvm to avoid system gcc
	SPACK_USER_CONFIG_PATH=packages spack compiler find --scope=user $$(spack -e compilers find --format '{prefix}' gcc llvm)

packages/config.yaml:
	SPACK_USER_CONFIG_PATH=packages spack config --scope=user add config:install_tree:root:$(INSTALLDIR)/opt/packages
	SPACK_USER_CONFIG_PATH=packages spack config --scope=user add modules:default:roots:tcl:$(INSTALLDIR)/modules/packages

packages/packages.yaml:
	touch packages/packages.yaml
	#SPACK_USER_CONFIG_PATH=packages spack external find --scope=user $(external_packages)

packages/spack.lock: packages/spack.yaml packages/config.yaml packages/packages.yaml packages/compilers.yaml
	spack python mixed_compiler_creator.py packages/compilers.yaml
	spack -e packages concretize --force

packages/spack.mk: packages/spack.lock
	spack -e packages env depfile --make-target-prefix packages/generated -o $@

packages/generated/modules: packages/generated/env
	spack -e packages module tcl refresh -y
	touch packages/generated/modules

ifeq (,$(filter clean,$(MAKECMDGOALS)))
include bootstrap/spack.mk

ifneq (,$(wildcard bootstrap/spack.mk))
#Try to get binutils into PATH
#export PATH := $(shell spack -e bootstrap find --format "{prefix}" binutils)/bin:$(PATH)
#export SHELL := env PATH=$(PATH) /bin/bash
#$(info    PATH is $(PATH))
include compilers/spack.mk
endif

ifneq (,$(wildcard compilers/spack.mk))
#Try to get binutils into PATH
#export PATH := $(shell spack -e bootstrap find --format "{prefix}" binutils)/bin:$(PATH)
#export SHELL := env PATH=$(PATH) /bin/bash
#$(info    PATH is $(PATH))
include packages/spack.mk
endif

endif
