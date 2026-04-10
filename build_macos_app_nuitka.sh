#!/usr/bin/env bash
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

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

PYTHON_VERSION="${PYMINFLUX_PYTHON_VERSION:-3.12}"

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required to build pyMINFLUX." 1>&2
    exit 1
fi

uv python install "${PYTHON_VERSION}"
uv sync --locked --extra dev --python "${PYTHON_VERSION}" --managed-python

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "${VENV_PYTHON}" ]]; then
    echo "Could not find the uv-managed Python environment at ${VENV_PYTHON}." 1>&2
    exit 1
fi

VERSION="$(
    "${VENV_PYTHON}" -c \
        "import pathlib, tomllib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['version'])"
)"

VISPY_GLSL_DIR="$(
    "${VENV_PYTHON}" -c \
        "import os, vispy; print(os.path.join(os.path.dirname(vispy.__file__), 'glsl'))"
)"

if [[ -z "${VISPY_GLSL_DIR}" ]]; then
    echo "Could not determine vispy glsl directory." 1>&2
    exit 1
fi

rm -rf build dist

"${VENV_PYTHON}" -m nuitka pyminflux/main.py -o pyMINFLUX \
    --clang \
    --assume-yes-for-downloads \
    --standalone \
    --macos-create-app-bundle \
    --macos-signed-app-name="ch.ethz.pyminflux" \
    --macos-app-name="pyMINFLUX" \
    --macos-app-version="${VERSION}" \
    --macos-app-icon=pyminflux/ui/assets/Logo_v3.icns \
    --include-module=scipy.special._special_ufuncs \
    --include-module=deprecated \
    --include-module=vispy.app.backends._pyside6 \
    --include-module=pydoc \
    --include-data-dir="${VISPY_GLSL_DIR}=vispy/glsl" \
    --enable-plugin=pylint-warnings \
    --enable-plugin=pyside6 \
    --noinclude-default-mode=nofollow \
    --output-dir=./dist

mv ./dist/main.app ./dist/pyMINFLUX.app