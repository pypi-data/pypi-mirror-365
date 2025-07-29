#!/bin/bash

set -ex

flake8
mypy knowit
mypy tests
pytest --cov-report term --cov-report html --cov knowit -vv tests