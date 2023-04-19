#
# Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich. All rights reserved.
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
