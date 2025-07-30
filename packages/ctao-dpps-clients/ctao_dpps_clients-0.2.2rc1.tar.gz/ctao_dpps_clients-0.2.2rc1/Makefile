###
export CHART_NAME=dpps
export CHART_LOCATION=chart
include dpps-aiv-toolkit/Makefile


export TEST_ARTIFACTS_PATH ?= $(PWD)
export TEST_REPORT_CONFIG ?= $(PWD)/config.yml


DATAPIPE_VERSION=$(shell grep DATAPIPE_VERSION aiv-config.yml | cut -d':' -f2 | xargs)
CALIBPIPE_VERSION=$(shell grep CALIBPIPE_VERSION aiv-config.yml | cut -d':' -f2 | xargs)

# for some reason, here the default is different
export DEV_IMAGE_SUFFIX=-clients
export DEV_DOCKER_EXTRA_ARGS=\
	--build-arg DATAPIPE_VERSION=${DATAPIPE_VERSION} \
	--build-arg=CALIBPIPE_VERSION=${CALIBPIPE_VERSION}
