#!/usr/bin/make
#
# Makefile for Debian
#
VERSION=`cat version.txt|cut -d/ -f2`
DEV_VERSION=`cat version.txt|cut -d/ -f2|cut -d. -f1,2,3`
deb:
	git-dch -a --ignore-branch
	dch -v $(VERSION).$(BUILD_NUMBER) release --no-auto-nmu
	dpkg-buildpackage -b -uc -us

deb-staging:
	git-dch -a --ignore-branch
	dch -v $(DEV_VERSION).dev$(BUILD_NUMBER) release --no-auto-nmu
	dpkg-buildpackage -b -uc -us

.PHONY: deb

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 .
	./bin/python bootstrap.py

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -vt 5;
