# pyMINFLUX

Reader, analyzer, and viewer of MINFLUX raw data.

## Installation

Compiled executables (apps) for Linux, macOS and Windows can be downloaded from the [release page](#). 

**Please note**: since pyMINFLUX on macOS comes from an *unidentified developer*, you might need to make an exception in the macOS security settings when launching it for the first time. To do this, right-click on the application icon and select `Open`. After this initial setup, you can simply double-click the icon to launch pyMINFLUX normally.

## For developers and tinkerers

pyMINFLUX is compatible with and tested on Python 3.10 and 3.11. For development, it is recommended to install pyMINFLUX in editable mode in a [conda](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) environment as follows:

### Windows and Linux

```bash
conda create -n pyminflux-env python=3.10  # or 3.11
conda activate pyminflux-env
git clone https://git.bsse.ethz.ch/pontia/pyminflux ${/path/to/pyminflux}
cd ${/path/to/pyminflux}
python -m pip install -e .
```

### macOS

openGL support in recent macOS requires `pyopengl` to be installed with `conda` instead of `pip`.

```bash
conda create -n pyminflux-env python=3.10  # or 3.11
conda activate pyminflux-env
git clone https://git.bsse.ethz.ch/pontia/pyminflux ${/path/to/pyminflux}
cd ${/path/to/pyminflux}
conda install pyopengl       # This is specific to macOS
python -m pip install -e .
```

### Running pyMinFlux from console

```bash
cd ${/path/to/pyminflux}
python pyminflux/main.py
```

## Official website and documentation

The official pyMINFLUX website is on https://pyminflux.ethz.ch.
