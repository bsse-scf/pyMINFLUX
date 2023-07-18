# ![](pyminflux/ui/assets/Logo_v3_small.png)&nbsp;&nbsp;&nbsp;pyMINFLUX

Reader, analyzer, and viewer of MINFLUX raw data.

<p align="center">
  <img width="800" src="https://pyminflux.ethz.ch/img/pyminflux.png">
</p>

## Installation

### Apps

Compiled executables (apps) for Linux, macOS and Windows can be downloaded from the [release page](https://github.com/bsse-scf/pyMINFLUX/releases/latest). 

**Please note**: since pyMINFLUX on macOS comes from an *unidentified developer*, you might need to make an exception in the macOS security settings when launching it for the first time. To do this, right-click on the application icon and select `Open`. After this initial setup, you can simply double-click the icon to launch pyMINFLUX normally.

### pip

The latest version of pyMINFLUX can also be installed from [pypi.org](https://pypi.org/project/pyminflux/). pyMINFLUX is compatible with and tested on Python 3.10 and 3.11. It is recommended to install pyMINFLUX in a conda environment as follows:

```sh
$ conda create -n pyminflux-env python=3.10  # or 3.11
$ conda activate pyminflux-env
$ pip install --upgrade pyminflux
```

pyMINFLUX can then easily be run from the command line:

```sh
$ pyminflux
```

## For developers and tinkerers

pyMINFLUX is compatible with and tested on Python 3.10 and 3.11. For development, it is recommended to install pyMINFLUX in editable mode in a [conda](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) environment as follows:

### Windows and Linux

```sh
$ conda create -n pyminflux-env python=3.10  # or 3.11
$ conda activate pyminflux-env
$ git clone https://github.com/bsse-scf/pyMINFLUX /path/to/pyminflux
$ cd /path/to/pyminflux
$ python -m pip install -e .
```

### macOS

openGL support in recent macOS requires `pyopengl` to be installed with `conda` instead of `pip`.

```sh
$ conda create -n pyminflux-env python=3.10  # or 3.11
$ conda activate pyminflux-env
$ git clone https://github.com/bsse-scf/pyMINFLUX /path/to/pyminflux
$ cd /path/to/pyminflux
$ conda install pyopengl       # This is specific to macOS
$ python -m pip install -e .
```

### Running pyMINFLUX from console

```sh
$ cd /path/to/pyminflux
$ python pyminflux/main.py  # As a Python script, or
$ pyminflux                 # as a standalone tool
```

### Using the pyMINFLUX API from Python scripts or Jupyter Notebooks

The graphical user interface is not the only way to use pyMINFLUX. Indeed, the pyMINFLUX core library can be integrated in Python scripts or Jupyter Notebooks. The documentation for the pyMIMFLUX core API can be found on [https://pyminflux.ethz.ch/api/pyminflux/](https://pyminflux.ethz.ch/api/pyminflux/); an example Jupyter Notebook is [bundled with the code](/examples/processing.ipynb).

## User manual

The user manual is hosted in the [project wiki](https://github.com/bsse-scf/pyMINFLUX/wiki/pyMINFLUX-user-manual).

## Official website

The official pyMINFLUX website is on https://pyminflux.ethz.ch.

## pyMINFLUX mailing list

Join the [pyMINFLUX mailing list](https://sympa.ethz.ch/sympa/subscribe/pyminflux) for release announcements and further discussions.

## Citing pyMINFLUX

If you use pyMINFLUX in your research, please cite this repository as follows:

> Aaron Ponti, Javier Casares Arias, & Thomas Horn. (2023). pyMINFLUX. Zenodo. [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7895501.svg)](https://doi.org/10.5281/zenodo.7895501)



