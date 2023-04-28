#!/bin/sh
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

# Use on macOS

s=$1
ICON_NAME="${s%.*}.icns"
echo "Converting $1 to $ICON_NAME..."

# Create an icon directory to work in
ICONS_DIR="tempicon.iconset"
mkdir $ICONS_DIR

# Create all other images sizes
sips -z 1024 1024 $1 --out "$ICONS_DIR/icon_512x512@2x.png"
sips -z 512  512  "$ICONS_DIR/icon_512x512@2x.png" --out "$ICONS_DIR/icon_512x512.png"
sips -z 512  512  "$ICONS_DIR/icon_512x512@2x.png" --out "$ICONS_DIR/icon_256x256@2x.png"
sips -z 256  256  "$ICONS_DIR/icon_512x512@2x.png" --out "$ICONS_DIR/icon_256x256x.png"
sips -z 256  256  "$ICONS_DIR/icon_512x512@2x.png" --out "$ICONS_DIR/icon_128x128@2x.png"
sips -z 128  128  "$ICONS_DIR/icon_512x512@2x.png" --out "$ICONS_DIR/icon_128x128.png"
sips -z 64   64   "$ICONS_DIR/icon_512x512@2x.png" --out "$ICONS_DIR/icon_64x64.png"
sips -z 32   32   "$ICONS_DIR/icon_512x512@2x.png" --out "$ICONS_DIR/icon_32x32.png"
sips -z 32   32   "$ICONS_DIR/icon_512x512@2x.png" --out "$ICONS_DIR/icon_16x16@2x.png"
sips -z 16   16   "$ICONS_DIR/icon_512x512@2x.png" --out "$ICONS_DIR/icon_16x16.png"

# Create the icns file
iconutil -c icns $ICONS_DIR

# remove the temporary directory
rm -rf $ICONS_DIR

# rename icns
mv tempicon.icns $ICON_NAME
