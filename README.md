# pyMINFLUX

Reader, processor, and viewer of MINFLUX raw data.

## Installation

For the moment, it is recommended to install in editable mode as follows:

### Windows and Linux

```bash
conda create -n pyminflux-env python=3.10
git clone https://git.bsse.ethz.ch/pontia/pyminflux ${/path/to/pyminflux}
cd ${/path/to/pyminflux}
python -m pip install -e .
```

### Recent macOS

```bash
conda create -n pyminflux-env python=3.10
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

