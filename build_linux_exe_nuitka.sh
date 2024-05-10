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

VERSION=0.4.1
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

# Install nuitka
python -m pip install nuitka ordered_set zstandard patchelf

# Install dependencies
poetry install

# Delete build and dist folders
rm -fR build
rm -fR dist

# Install static python lib
conda install libpython-static -y

# Build the executable
python -m nuitka pyminflux/main.py -o pyMINFLUX \
--assume-yes-for-downloads \
--disable-console \
--noinclude-default-mode=error \
--standalone \
--onefile \
--linux-icon=pyminflux/ui/assets/Logo_v3.ico \
--enable-plugin=pylint-warnings \
--enable-plugin=pyside6 \
--noinclude-default-mode=nofollow \
--file-version=$VERSION \
--product-version=$VERSION \
--remove-output \
--output-dir=./dist

# Move into "pyMINFLUX" directory
mkdir -p dist/target
mv dist/pyMINFLUX dist/target/
mv dist/target dist/pyMINFLUX

# Copy the icon
cp pyminflux/ui/assets/Logo_v3.png dist/pyMINFLUX/icon.png

# Zip the archive
cd dist
zip -r pyMINFLUX_${VERSION}_linux.zip pyMINFLUX
cd ..

# Remove the conda environment
conda deactivate
conda env remove -n pyminflux-build -y
