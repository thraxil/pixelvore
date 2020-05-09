# default config values that can all be overridden
VE ?= ./ve
MANAGE ?= ./manage.py
FLAKE8 ?= $(VE)/bin/flake8
SYS_PYTHON ?= python3
PIP ?= $(VE)/bin/pip3
PIP_VERSION ?= 20.1
SENTINAL ?= $(VE)/sentinal
REQUIREMENTS ?= requirements.txt
VIRTUALENV ?= virtualenv.py
SUPPORT_DIR ?= requirements/virtualenv_support/

JS_FILES ?= media/js/
TAG ?= latest
IMAGE ?= $(REPO)/$(APP):$(TAG)

MAX_COMPLEXITY ?= 10

