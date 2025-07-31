# Annular

| fair-software.eu recommendations |                                                                                                                                                                                 |
|:---------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| (1/5) code repository            | [![gitlab repo badge](https://img.shields.io/badge/gitlab-repo-000.svg?logo=gitlab&labelColor=gray&color=blue)][repo-url]                                                       |
| (2/5) license                    | [![gitlab license badge](https://img.shields.io/gitlab/license/demoses/annular?gitlab_url=https://gitlab.tudelft.nl)][repo-url]                                                 |
| (3/5) community registry         | [![RSD](https://img.shields.io/badge/rsd-annular-00a3e3.svg)][demoses-rsd]                                                                                             |
| (4/5) citation                   | [![DOI][Zenodo-badge]][Zenodo-url]                                                                                                                                              |
| (5/5) checklist                  |                                                                                                                                                                                 |
| howfairis                        | [![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu) |
| **Other best practices**         |                                                                                                                                                                                 |
| Software Version                 | ![Software Version](https://img.shields.io/badge/version-0.3.0-green)                                                                                                           |
| Supported Python versions        | ![Supported Python Versions][py-versions-badge]                                                                                                                                 |


## Introduction

Annular is a setup for running coupled energy system models with the aim of modeling flexibility scheduling and the policy regulations that affect the behavior of flexibility providers.

### Name
**Why the name 'annular'?**

'Annular' means 'in the shape of a ring', with which we specifically think of the rings of Saturn, containing many moons or in other words satellites, just like the satellite models interacting with the central market model.

## Installation

You can install `annular` directly from [PyPI](https://pypi.org/project/annular/):

```bash
# Best practice: install in a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Use `source .venv/Scripts/activate` on Windows

python3 -m pip install annular
```

Then you can run the `run_local.py` file as a commandline tool to run coupled simulations specified by config files.

```bash
python run_local.py examples/data/energy_model_coupling.ymmsl
# ...
# intermediate output appears here
# ...
```

Result files will appear in a `results/<CONFIG_NAME>_<TIMESTAMP>/` folder, where `<CONFIG_NAME>` is the name as defined
in the configuration file, and `<TIMESTAMP>` is a timestamp of when your experiment was run. This folder will include a
copy of the used configuration file for archival purposes.

See the built-in help for further details:

```bash
$ python3 run_local.py --help
usage: run_local.py [-h] [config_files ...]

positional arguments:
  config_files  Configuration files to run simulations for.

options:
  -h, --help    show this help message and exit
```

NOTE: The code is tested and compatible with python versions 3.10 and 3.11.

## Contributing

If you want to contribute to the development of annular,
have a look at the [contribution guidelines](CONTRIBUTING.md).

Further instructions can be found in[`README.dev.md`](README.dev.md)

## Citation

For citation information, see [`CITATION.cff`](CITATION.cff)

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).

[repo-url]:             https://gitlab.tudelft.nl/demoses/annular
[demoses-rsd]:          https://www.research-software.nl/projects/demoses
[py-versions-badge]:    https://img.shields.io/badge/python-3.10%20%7C%203.11-blue
[Zenodo-url]:           https://doi.org/10.5281/zenodo.13144649
[Zenodo-badge]:         https://zenodo.org/badge/DOI/10.5281/zenodo.13144649.svg
