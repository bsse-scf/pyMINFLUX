# pyMINFLUX

Reader, analyzer, and viewer of MINFLUX raw data.

## Installation

For the moment, it is recommended to install pyMINFLUX in editable mode in a [conda](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) environment as follows:

### Windows and Linux

```bash
conda create -n pyminflux-env python=3.10
conda activate pyminflux-env
git clone https://git.bsse.ethz.ch/pontia/pyminflux ${/path/to/pyminflux}
cd ${/path/to/pyminflux}
python -m pip install -e .
```

### Recent macOS

openGL support in recent macOS requires `pyopengl` to be installed with `conda` instead of `pip`.

```bash
conda create -n pyminflux-env python=3.10
conda activate pyminflux-env
git clone https://git.bsse.ethz.ch/pontia/pyminflux ${/path/to/pyminflux}
cd ${/path/to/pyminflux}
conda install pyopengl       # This is different
python -m pip install -e .
```

## Running pyMinFlux

```bash
cd ${/path/to/pyminflux}
python pyminflux/main.py
```

