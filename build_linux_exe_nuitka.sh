#!/bin/bash
# Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
#  limitations under the License.
#

VERSION=0.5.0
PYTHON_VERSION=3.12

if [[ -z "$ANACONDA_HOME" ]]; then
    echo "Please set environment variable ANACONDA_HOME." 1>&2
    exit 1
fi

# Source conda.sh
source $ANACONDA_HOME/etc/profile.d/conda.sh

# Create and activate a dedicated env
conda create -n pyminflux-build python=$PYTHON_VERSION -y
conda activate pyminflux-build

# Install nuitka
python -m pip install nuitka ordered_set zstandard patchelf

# Install static python lib
conda install libpython-static -y

# Install dependencies
poetry install

# Determine the path to the vispy glsl directory
VISPY_GLSL_DIR=$(python -c "import vispy, os; print(os.path.join(os.path.dirname(vispy.__file__), 'glsl'))")

# Check if the path was found
if [ -z "$VISPY_GLSL_DIR" ]; then
    echo "Could not determine vispy glsl directory"
    exit 1
fi

# Delete build and dist folders
rm -fR build
rm -fR dist

# Build the executable
python -m nuitka pyminflux/main.py -o pyMINFLUX \
--assume-yes-for-downloads \
--noinclude-default-mode=error \
--standalone \
--include-module=pydoc \
--include-module=scipy.special._special_ufuncs \
--include-module=vispy.app.backends._pyside6 \
--include-module=pydoc \
--include-data-dir="$VISPY_GLSL_DIR=vispy/glsl" \
--linux-icon=pyminflux/ui/assets/Logo_v3.ico \
--enable-plugin=pylint-warnings \
--enable-plugin=pyside6 \
--noinclude-default-mode=nofollow \
--file-version=$VERSION \
--product-version=$VERSION \
--remove-output \
--follow-imports \
--static-libpython=yes \
--output-dir=./dist

# Rename output folder
mv dist/main.dist dist/pyMINFLUX

# Create plugins sub-folder
mkdir dist/pyMINFLUX/plugins

# Copy Hello, World! plugin
cp -R plugins/hello_world dist/pyMINFLUX/plugins
rm -fR dist/pyMINFLUX/plugins/hello_world/__pycache__

# Copy the icon
cp pyminflux/ui/assets/Logo_v3.png dist/pyMINFLUX/icon.png

# Remove the conda environment
conda deactivate
conda env remove -n pyminflux-build -y
