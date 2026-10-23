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

docker-image:
	docker build --pull -t harbor.imio.be/docs/webservicejson:latest .

up:
	docker compose up

start:
	docker compose start

stop:
	docker compose stop

dev:
	docker compose -f docker-compose-dev.yaml up

cleanup:
	docker run --rm --network="imiowebservicejson_default" -v $(PWD)/data:/home/imio/data -v $(PWD)/config:/home/imio/config harbor.imio.be/docs/webservicejson:latest /home/imio/imio.webservice.json/.venv/bin/file_cleanup /home/imio/config/development.ini 0
