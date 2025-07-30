# OU Book Theme

[![PyPI - Version](https://img.shields.io/pypi/v/ou-book-theme.svg)](https://pypi.org/project/ou-book-theme)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ou-book-theme.svg)](https://pypi.org/project/ou-book-theme)

-----

## Installation

```console
pip install ou-book-theme
```

Full documentation can be found at [https://docs.ocl.open.ac.uk/ou-book-theme/latest](https://docs.ocl.open.ac.uk/ou-book-theme/latest).

## Development

To reduce any code formatting and layouting issues, the project uses the [Ruff linter and formatter](https://docs.astral.sh/ruff/).

To ensure that your code follows the formatting, a [pre-commit hook](https://pre-commit.com/) is provided, which can
be installed via

```console
pre-commit install
```

The project uses [hatch](https://hatch.pypa.io) to manage the Python development environment. Additionally the build
process requires [Node.js](https://nodejs.org/en). After installing the pre-requisites, you can run the development
server with the following command:

```console
hatch run server
```
