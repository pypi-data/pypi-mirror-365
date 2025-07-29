# orkg-pypi
[![Python version](https://img.shields.io/pypi/pyversions/orkg.svg)](https://img.shields.io/pypi/pyversions/orkg.svg)
[![pipeline status](https://gitlab.com/TIBHannover/orkg/orkg-pypi/badges/master/pipeline.svg)](https://gitlab.com/TIBHannover/orkg/orkg-pypi/-/commits/master)
[![Documentation Status](https://readthedocs.org/projects/orkg/badge/?version=latest)](https://orkg.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/orkg.svg)](https://badge.fury.io/py/orkg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![flake8](https://img.shields.io/badge/flake8-enabled-brightgreen)](https://github.com/PyCQA/flake8)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A python client interacting with the ORKG API and sprinkling some python magic on top.

The package a implements many of the API calls described in the [documentation](http://tibhannover.gitlab.io/orkg/orkg-backend/api-doc/), and provides a set of extra features like graph pythonic objects and dynamic instantiation of entities from specifications.

You can find details about how-to use the package on [Read the Docs](https://orkg.readthedocs.io/en/latest/index.html).

Developers, please note that you need to install the pre-commit script via
```bash
pip install -r requirements.txt
pre-commit install
```
And check the [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

# Noteworthy Contributors

Special thanks to the following awesome people
- Allard Oelen
- Kheir Eddine Farfar
- Omar Arab Oghli
- Julia Evans
