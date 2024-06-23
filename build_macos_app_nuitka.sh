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
python -m pip install nuitka ordered_set zstandard # patchelf  (Linux)

# Install dependencies
poetry install

# Delete build and dist folders
rm -fR build
rm -fR dist

# Build the app
python -m nuitka pyminflux/main.py -o pyMINFLUX \
--clang \
--assume-yes-for-downloads \
--disable-console \
--noinclude-default-mode=error \
--standalone \
--macos-create-app-bundle \
--macos-signed-app-name="ch.ethz.pyminflux" \
--macos-app-name="pyMINFLUX" \
--macos-app-version=$VERSION \
--macos-app-icon=pyminflux/ui/assets/Logo_v3.icns \
--enable-plugin=pylint-warnings \
--enable-plugin=pyside6 \
--noinclude-default-mode=nofollow \
--remove-output \
--output-dir=./dist

# Rename the bundle
mv ./dist/main.app ./dist/pyMINFLUX.app

# Zip the archive
cd ./dist
zip -r pyMINFLUX_${VERSION}_macos.zip pyMINFLUX.app
cd ..

# Remove the conda environment
conda deactivate
conda env remove -n pyminflux-build -y
