# Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
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

VERSION=0.3.0
PYTHON_VERSION=3.11

if [[ -z "$ANACONDA_HOME" ]]; then
    echo "Please set environment variable ANACONDA_HOME." 1>&2
    exit 1
fi

# Source conda.sh
source $ANACONDA_HOME/etc/profile.d/conda.sh

# Create and activate a dedicated env
conda create -n pyminflux-build python=$PYTHON_VERSION -y
conda activate pyminflux-build

# Install dependencies
poetry install

# Delete build and dist folders
rm -fR build
rm -fR dist

# Build the executable
pyinstaller pyminflux/main.py \
--clean \
--windowed \
--hidden-import="sklearn.neighbors._typedefs" \
--hidden-import="sklearn.metrics._pairwise_distances_reduction._datasets_pair" \
--hidden-import="sklearn.metrics._pairwise_distances_reduction._middle_term_computer" \
--icon pyminflux/ui/assets/Logo_v3.png \
--noconsole \
--name pyMINFLUX \
--noconfirm

# Copy the icon
cp pyminflux/ui/assets/Logo_v3.png dist/pyMINFLUX

# Zip the archive
cd dist
zip -r pyMINFLUX_${VERSION}_linux.zip pyMINFLUX
cd ..

# Remove the conda environment
conda deactivate
conda env remove -n pyminflux-build -y
