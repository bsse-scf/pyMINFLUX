#!/bin/bash
# Copyright (c) 2022 - 2026 D-BSSE, ETH Zurich.
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

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: ./build_docs.sh /path/to/docs/folder"
    exit 1
fi

output_dir="$1"
current_docs_dir="$output_dir/pyminflux"

if [ -d "$current_docs_dir" ]; then
    rm -rf "$current_docs_dir"
fi

# Build documentation
uv run pdoc3 pyminflux --html --force --output-dir "$output_dir" --template-dir templates

# pdoc adds these private module paths to the generated HTML for public classes.
find "$current_docs_dir" -name "*.html" -exec perl -0pi -e 's/pyminflux\.reader\._reader\.MinFluxReader/pyminflux.reader.MinFluxReader/g; s/pyminflux\.processor\._processor\.MinFluxProcessor/pyminflux.processor.MinFluxProcessor/g' {} +

