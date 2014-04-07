#!/usr/bin/make
#
# Makefile for Debian
#
VERSION=`cat version.txt`
deb:
	git-dch -a --ignore-branch
	dch -v $(VERSION) release --no-auto-nmu
	dpkg-buildpackage -b -uc -us

.PHONY: deb
