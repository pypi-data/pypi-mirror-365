.PHONY: default help package push

APP_NAME=mcp-multi-weather
IMAGE_NAME=igalarzab/mcp-multi-weather
REGISTRY=ghcr.io

# Not constant variables
GIT_COMMIT=$(shell git rev-parse HEAD)
GIT_SHORT_COMMIT=$(shell git rev-parse --short HEAD)
BUILD_DATE=$(shell date -u '+%Y-%m-%dT%H:%M:%SZ')
VERSION=v$(shell uv version --short)

default: package

help:
	@echo 'Management commands:'
	@echo
	@echo 'Usage:'
	@echo '    make package           Build final docker image'
	@echo '    make push              Push tagged images to registry'
	@echo

package:
	@echo "Building ${APP_NAME}:${VERSION}"
	docker build \
	    --build-arg VERSION=${VERSION} \
	    --build-arg GIT_COMMIT=${GIT_COMMIT} \
	    --build-arg BUILD_DATE=${BUILD_DATE} \
	    --tag ${REGISTRY}/${IMAGE_NAME}:${VERSION} \
	    --tag ${REGISTRY}/${IMAGE_NAME}:latest \
	    .

push:
	@echo "Pushing docker images to registry: latest, ${VERSION}"
	docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
	docker push ${REGISTRY}/${IMAGE_NAME}:latest
