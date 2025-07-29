[![Python Versions](https://img.shields.io/pypi/pyversions/hpc.png)](https://img.shields.io/pypi/pyversions/hpc)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
![GitHub last commit](https://img.shields.io/github/last-commit/Serapieum-of-alex/hpc)
![GitHub forks](https://img.shields.io/github/forks/Serapieum-of-alex/hpc?style=social)
![GitHub Repo stars](https://img.shields.io/github/stars/Serapieum-of-alex/hpc?style=social)

[![tests](https://github.com/Serapieum-of-alex/hpc/actions/workflows/tests.yml/badge.svg)](https://github.com/Serapieum-of-alex/hpc/actions/workflows/tests.yml)
[![pypi-release](https://github.com/Serapieum-of-alex/hpc/actions/workflows/pypi-release.yml/badge.svg)](https://github.com/Serapieum-of-alex/hpc/actions/workflows/pypi-release.yml)
[![Deploy MkDocs](https://github.com/Serapieum-of-alex/hpc/actions/workflows/github-pages-mkdocs.yml/badge.svg)](https://github.com/Serapieum-of-alex/hpc/actions/workflows/github-pages-mkdocs.yml)
[![GitHub Release](https://github.com/Serapieum-of-alex/hpc/actions/workflows/create-release.yml/badge.svg)](https://github.com/Serapieum-of-alex/hpc/actions/workflows/create-release.yml)

Full documentation is available at [serapieum-of-alex.github.io/hpc](https://serapieum-of-alex.github.io/hpc//)

Current release info
====================
- conda-forge feedstock: [hpc](https://anaconda.org/conda-forge/hpc)
  - [github feedstock](https://github.com/conda-forge/hpc-feedstock)

| Name | Downloads                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Version                                                                                                                                                                                                                                                                                                                               | Platforms |
| --- |--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| --- |
| [![Conda Recipe](https://img.shields.io/badge/recipe-hpc-green.svg)](https://anaconda.org/conda-forge/hpc) | [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/hpc.svg)](https://anaconda.org/conda-forge/hpc) [![Downloads](https://pepy.tech/badge/hpc-utils)](https://pepy.tech/project/hpc) [![Downloads](https://pepy.tech/badge/hpc-utils/month)](https://pepy.tech/project/hpc)  [![Downloads](https://pepy.tech/badge/hpc-utils/week)](https://pepy.tech/project/hpc)  ![PyPI - Downloads](https://img.shields.io/pypi/dd/hpc-utils?color=blue&style=flat-square) ![GitHub all releases](https://img.shields.io/github/downloads/Serapieum-of-alex/hpc/total) ![GitHub release (latest by date)](https://img.shields.io/github/downloads/Serapieum-of-alex/hpc/0.1.4/total) | [![Conda Version](https://img.shields.io/conda/vn/conda-forge/hpc.svg)](https://anaconda.org/conda-forge/hpc) [![PyPI version](https://badge.fury.io/py/hpc-utils.svg)](https://badge.fury.io/py/hpc-utils) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/hpc/badges/version.svg)](https://anaconda.org/conda-forge/hpc) | [![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/hpc.svg)](https://anaconda.org/conda-forge/hpc) [![Join the chat at https://gitter.im/Hapi-Nile/Hapi](https://badges.gitter.im/Hapi-Nile/Hapi.svg)](https://gitter.im/Hapi-Nile/Hapi?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) |

hpc - Remote Sensing package
=====================================================================
**hpc** is a numpy utility package

Main Features
-------------
  - indixing numpy arrays in fast manner without using loops


Installing hpc
===============

Installing `hpc` from the `conda-forge` channel can be achieved by:

```
conda install -c conda-forge hpc
```

It is possible to list all of the versions of `hpc` available on your platform with:

```
conda search hpc --channel conda-forge
```

## Install from Github
to install the last development to time you can install the library from github
```
pip install git+https://github.com/MAfarrag/hpc
```

## pip
to install the last release you can easly use pip
```
pip install hpc-utils==0.1.5
```

Quick start
===========

```
  >>> import hpc
```
