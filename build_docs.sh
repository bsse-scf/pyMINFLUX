#!/bin/bash
# Copyright (c) 2022 - 2025 D-BSSE, ETH Zurich.
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
# limitations under the License.

if [ "$#" != "1" ]; then
    echo "Usage: ./build_docs.sh /path/to/docs/folder"
    exit
fi

if [ -d "$1" ]
then
    dir_name=$(basename "$1")
    parent_path=$(dirname "$1")
    current_date=$(date +%Y%m%d_%H%M%S)
    mv "$1" "$parent_path/${dir_name}_$current_date"
    echo "$1 renamed to $parent_path/${dir_name}_$current_date"
fi

# Build documentation
pdoc3 pyminflux --html --force --output-dir "$1" --template-dir templates

# Wrong references are added to the code -- unclear why
find . -name "*.html" -exec sed -i 's/pyminflux.reader._reader.MinFluxReader/pyminflux.reader.MinFluxReader/g' {} \;
find . -name "*.html" -exec sed -i 's/pyminflux.processor._processor.MinFluxProcessor/pyminflux.processor.MinFluxProcessor/g' {} \;

