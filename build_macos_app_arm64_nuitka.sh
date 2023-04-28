#
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
#


# To build, use the following command
python -m nuitka \
--jobs=8 \
--include-module=OpenGL \
--noinclude-default-mode=error \
--follow-imports \
--nofollow-import-to=tkinter \
--disable-console \
--macos-create-app-bundle \
--macos-app-icon=pyminflux/ui/assets/Logo_v3.icns \
--assume-yes-for-downloads \
--enable-plugin=pylint-warnings \
--standalone pyminflux/main.py \
--enable-plugin=numpy \
--enable-plugin=pyside6 \
--output-dir=./dist
