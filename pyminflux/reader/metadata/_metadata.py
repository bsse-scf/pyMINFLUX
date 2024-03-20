#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.
from dataclasses import dataclass
from typing import Union


@dataclass
class NativeMetadata:
    """Metadata associated to `.pmx` native pyMINFLUX file format.

    Version 2.0
    -----------
        time_thresholds: Union[None, tuple[float, float]]
        tr_len_thresholds: Union[None, tuple[int, int]]
        dwell_time: float
        is_tracking: bool
        scale_bar_size: float
        (+ version 1.0)

    Version 1.0
    -----------
        z_scaling_factor: float
        min_trace_length: int
        efo_thresholds: tuple[int, int]
        cfr_thresholds: tuple[float, float]
        num_fluorophores: int
    """

    cfr_thresholds: Union[None, tuple[float, float]]
    dwell_time: float
    efo_thresholds: Union[None, tuple[int, int]]
    is_tracking: bool
    min_trace_length: int
    num_fluorophores: int
    scale_bar_size: float
    time_thresholds: Union[None, tuple[float, float]]
    tr_len_thresholds: Union[None, tuple[float, float]]
    z_scaling_factor: float
