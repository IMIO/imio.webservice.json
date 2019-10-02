#!/usr/bin/make
#
# Makefile for Debian
#
VERSION=`cat version.txt|cut -d/ -f2`
DEV_VERSION=`cat version.txt|cut -d/ -f2|sed s/.dev.//|cut -d. -f1,2,3`
PWD=`pwd`
deb:
	git-dch -a --ignore-branch
	dch -v $(VERSION).$(BUILD_NUMBER) release --no-auto-nmu
	dpkg-buildpackage -b -uc -us

deb-staging:
	git-dch -a --ignore-branch
	dch -v $(DEV_VERSION).$(BUILD_NUMBER) release --no-auto-nmu
	dpkg-buildpackage -b -uc -us

.PHONY: deb

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 .
	./bin/pip install -r requirements.txt

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -vt 5;

docker-image:
	docker build --pull -t webservicejson/mutual:latest .

up:
	docker-compose up

start:
	docker-compose start

stop:
	docker-compose stop

dev:
	docker-compose -f docker-compose-dev.yaml up

cleanup:
	docker run --rm --network="imiowebservicejson_default" -v $(PWD)/data:/home/imio/data -v $(PWD)/config:/home/imio/config docker-staging.imio.be/webservicejson/mutual:latest /home/imio/imio.webservice.json/bin/file_cleanup /home/imio/config/development.ini 0
