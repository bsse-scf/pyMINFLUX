#
# Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich. All rights reserved.
#

# To build, use the following command
pyinstaller pyminflux/main.py \
--clean \
--windowed \
--hidden-import="sklearn.neighbors._typedefs" \
--icon pyminflux/ui/assets/Logo_v3.png \
--noconsole \
--name pyMINFLUX \
--noconfirm

# Copy the icon
cp pyminflux/ui/assets/Logo_v3.png dist/pyMINFLUX
