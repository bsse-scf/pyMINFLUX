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

# To build, use the following command: currently there appears to be an issue with pyqtgraph
pyinstaller pyminflux/main.py \
--windowed \
--hidden-import="sklearn.metrics._pairwise_distances_reduction._datasets_pair" \
--hidden-import="sklearn.metrics._pairwise_distances_reduction._middle_term_computer" \
--noconsole \
--icon pyminflux/ui/assets/Logo_v3.icns \
--name pyMINFLUX \
--target-architecture=arm64 \
--osx-bundle-identifier 'ch.ethz.pyminflux' \
--noconfirm
