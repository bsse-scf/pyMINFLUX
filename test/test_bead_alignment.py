#  Copyright (c) 2022 - 2026 D-BSSE, ETH Zurich.
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
#  limitations under the License.

import zipfile
from pathlib import Path

import numpy as np
import pytest

from pyminflux.correct import align_datasets_using_beads
from pyminflux.correct._bead_alignment import RigidTransform, TranslationTransform
# MinFluxDataset must be imported before combiner._combine to break the circular
# import that arises because combiner._combine → processor._dataset → processor.__init__
# → combiner._combine.
from pyminflux.processor._dataset import MinFluxDataset
from pyminflux.combiner._combine import combine_datasets_with_bead_alignment
from pyminflux.reader import MinFluxReader

# ─────────────────────────────────────────────────────────────────────────────
# Module-level test data
# ─────────────────────────────────────────────────────────────────────────────

# Three 2-D bead positions given as [z_nm, y_nm, x_nm] (z=0 for a 2-D dataset).
_BEAD_POSITIONS_ZYX = [
    [0.0,  100.0,  200.0],
    [0.0,  500.0, 1000.0],
    [0.0, 1500.0,  300.0],
]
_BEAD_NAMES = ["bead_A", "bead_B", "bead_C"]

# Known translation [dz, dy, dx] in nm applied to the moving dataset.
_OFFSET_ZYX_NM = np.array([0.0, 15.0, -10.0])


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_mbm_data(bead_positions_zyx_nm, bead_names=None, n_points=5, tim_start=0.0):
    """Return a ``{'mbm': {...}}`` dict with synthetic bead localizations.

    Parameters
    ----------
    bead_positions_zyx_nm:
        Iterable of [z_nm, y_nm, x_nm] positions in nanometres.
    bead_names:
        Optional list of bead name strings.  Defaults to ``bead_0``, ``bead_1``, …
    n_points:
        Number of time-point replicates per bead.
    tim_start:
        Value added to the ``tim`` column so the bead data can simulate a
        later acquisition (matching the ``tim`` offset on the processed dataframe).
    """
    if bead_names is None:
        bead_names = [f"bead_{i}" for i in range(len(bead_positions_zyx_nm))]

    rng = np.random.default_rng(seed=42)
    mbm = {}
    for i, (pos_nm, name) in enumerate(zip(bead_positions_zyx_nm, bead_names)):
        z_nm, y_nm, x_nm = pos_nm
        # mbm_dict_to_dataframe reads columns as [x, y, z] and multiplies by 1e9
        # to convert metres → nm, so we store values in metres here.
        pos_m = np.array([x_nm * 1e-9, y_nm * 1e-9, z_nm * 1e-9])
        noise_m = rng.normal(0, 1e-12, (n_points, 3))  # ~1 pm localisation noise

        mbm[i] = {
            "bead_name": name,
            "gri": i,
            "used": True,
            "points": {
                "gri": np.zeros(n_points, dtype=np.int32),
                "tim": np.arange(n_points, dtype=np.float64) * 0.1 + tim_start,
                "str": np.ones(n_points, dtype=np.float64),
                "xyz": np.tile(pos_m, (n_points, 1)) + noise_m,
            },
        }

    return {"mbm": mbm}


def _make_dataset(npy_path, tim_offset=0.0, mbm_data=None):
    """Create a :class:`MinFluxDataset` from *npy_path*.

    *tim_offset* is added to every ``tim`` value in the processed dataframe so
    that datasets simulating later acquisitions have non-overlapping timestamps.
    *mbm_data* is injected directly; the v1 .npy reader does not carry bead data.
    """
    reader = MinFluxReader(npy_path)
    df = reader.processed_dataframe.copy()
    if tim_offset > 0.0:
        df["tim"] = df["tim"] + tim_offset
    return MinFluxDataset(
        processed_dataframe=df,
        filename=npy_path,
        is_3d=reader.is_3d,
        is_tracking=reader.is_tracking,
        is_aggregated=reader.is_aggregated,
        z_scaling_factor=reader.z_scaling_factor,
        unit_scaling_factor=reader._unit_scaling_factor,
        dwell_time=reader.dwell_time,
        pool_dcr=reader.is_pool_dcr,
        version=reader.version,
        mbm_data=mbm_data,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=False)
def npy_path():
    """Return path to the 2-D test .npy file, extracting it from ZIP if needed."""
    npy = Path(__file__).parent / "data" / "230321-111601_minflux2D_3.npy"
    mat = Path(__file__).parent / "data" / "230321-111601_minflux2D_3.mat"
    zip_ = Path(__file__).parent / "data" / "input_multi_format.zip"
    if not npy.is_file() or not mat.is_file():
        with zipfile.ZipFile(zip_, "r") as zf:
            zf.extractall(Path(__file__).parent / "data")
    return npy


# ─────────────────────────────────────────────────────────────────────────────
# align_datasets_using_beads
# ─────────────────────────────────────────────────────────────────────────────

def test_align_datasets_using_beads_identity():
    """Identical bead sets: a RigidTransform is returned and residuals are sub-nm."""
    ref_mbm = _make_mbm_data(_BEAD_POSITIONS_ZYX, bead_names=_BEAD_NAMES)["mbm"]
    mov_mbm = _make_mbm_data(_BEAD_POSITIONS_ZYX, bead_names=_BEAD_NAMES)["mbm"]

    model = align_datasets_using_beads(ref_mbm, mov_mbm)

    assert model is not None
    assert isinstance(model, RigidTransform)

    pts = np.array(_BEAD_POSITIONS_ZYX, dtype=float)
    residuals = model.residuals(pts, pts)
    assert np.all(residuals < 1.0), "Residuals should be sub-nm for identical bead sets"


def test_align_datasets_using_beads_known_translation():
    """Moving beads shifted by a known offset: recovered transform aligns them within 1 nm."""
    ref_positions = np.array(_BEAD_POSITIONS_ZYX, dtype=float)
    mov_positions = ref_positions + _OFFSET_ZYX_NM

    ref_mbm = _make_mbm_data(ref_positions.tolist(), bead_names=_BEAD_NAMES)["mbm"]
    mov_mbm = _make_mbm_data(mov_positions.tolist(), bead_names=_BEAD_NAMES)["mbm"]

    model = align_datasets_using_beads(ref_mbm, mov_mbm)

    assert model is not None
    assert isinstance(model, RigidTransform)

    # Applying the model to the moving positions should recover the reference positions.
    transformed = model(mov_positions)
    assert np.allclose(transformed, ref_positions, atol=1.0), (
        "Transformed moving beads must match reference positions within 1 nm"
    )


def test_align_datasets_using_beads_manual_correspondence():
    """Explicit bead_correspondence with different names is honoured correctly."""
    ref_positions = np.array(_BEAD_POSITIONS_ZYX, dtype=float)
    mov_positions = ref_positions + _OFFSET_ZYX_NM

    ref_names = ["ref_A", "ref_B", "ref_C"]
    mov_names = ["mov_A", "mov_B", "mov_C"]
    # Maps moving bead name → reference bead name
    correspondence = {mn: rn for mn, rn in zip(mov_names, ref_names)}

    ref_mbm = _make_mbm_data(ref_positions.tolist(), bead_names=ref_names)["mbm"]
    mov_mbm = _make_mbm_data(mov_positions.tolist(), bead_names=mov_names)["mbm"]

    model = align_datasets_using_beads(ref_mbm, mov_mbm, bead_correspondence=correspondence)

    assert model is not None
    transformed = model(mov_positions)
    assert np.allclose(transformed, ref_positions, atol=1.0)


def test_align_datasets_using_beads_translation_only():
    """Fewer than 3 beads triggers the translation-only path → TranslationTransform."""
    ref_positions = [[0.0, 100.0, 200.0], [0.0, 500.0, 1000.0]]
    mov_positions = [[0.0, 115.0, 190.0], [0.0, 515.0, 990.0]]

    ref_mbm = _make_mbm_data(ref_positions, bead_names=["bead_A", "bead_B"])["mbm"]
    mov_mbm = _make_mbm_data(mov_positions, bead_names=["bead_A", "bead_B"])["mbm"]

    model = align_datasets_using_beads(ref_mbm, mov_mbm)

    assert model is not None
    assert isinstance(model, TranslationTransform)


def test_align_datasets_using_beads_no_common_beads():
    """No common bead names and no bead_correspondence → returns None."""
    ref_mbm = _make_mbm_data(
        _BEAD_POSITIONS_ZYX, bead_names=["ref_A", "ref_B", "ref_C"]
    )["mbm"]
    mov_mbm = _make_mbm_data(
        _BEAD_POSITIONS_ZYX, bead_names=["mov_A", "mov_B", "mov_C"]
    )["mbm"]

    model = align_datasets_using_beads(ref_mbm, mov_mbm)

    assert model is None


def test_align_datasets_using_beads_no_used_beads():
    """Beads marked used=False are skipped; with none remaining, returns None."""
    ref_mbm_data = _make_mbm_data(_BEAD_POSITIONS_ZYX, bead_names=_BEAD_NAMES)
    for entry in ref_mbm_data["mbm"].values():
        entry["used"] = False

    mov_mbm = _make_mbm_data(_BEAD_POSITIONS_ZYX, bead_names=_BEAD_NAMES)["mbm"]

    model = align_datasets_using_beads(ref_mbm_data["mbm"], mov_mbm)

    assert model is None


# ─────────────────────────────────────────────────────────────────────────────
# combine_datasets_with_bead_alignment
# ─────────────────────────────────────────────────────────────────────────────

def test_combine_datasets_with_bead_alignment(npy_path):
    """Combined dataset has all rows, non-overlapping tids, and distinct fluo IDs."""
    ref_positions = np.array(_BEAD_POSITIONS_ZYX, dtype=float)
    mov_positions = ref_positions + _OFFSET_ZYX_NM

    ref_mbm_data = _make_mbm_data(ref_positions.tolist(), bead_names=_BEAD_NAMES)
    mov_mbm_data = _make_mbm_data(mov_positions.tolist(), bead_names=_BEAD_NAMES)

    ref_ds = _make_dataset(npy_path, tim_offset=0.0, mbm_data=ref_mbm_data)
    tim_offset_for_moving = ref_ds.processed_dataframe["tim"].max() + 1.0
    mov_ds = _make_dataset(
        npy_path, tim_offset=tim_offset_for_moving, mbm_data=mov_mbm_data
    )

    combined = combine_datasets_with_bead_alignment(ref_ds, mov_ds)

    assert combined is not None, "combine should succeed with valid mbm_data"

    ref_n = len(ref_ds.processed_dataframe)
    mov_n = len(mov_ds.processed_dataframe)
    assert len(combined.processed_dataframe) == ref_n + mov_n, (
        "Combined dataframe must contain every row from both input datasets"
    )

    # TIDs of the moving half in the combined dataframe must not overlap with
    # TIDs from the reference half.
    ref_tids = set(ref_ds.processed_dataframe["tid"].unique())
    mov_tids_in_combined = set(
        combined.processed_dataframe.iloc[ref_n:]["tid"].unique()
    )
    assert ref_tids.isdisjoint(mov_tids_in_combined), (
        "Moving dataset tids must be offset to avoid collisions with reference tids"
    )

    # The reference and moving halves must carry distinct fluorophore IDs.
    ref_fluo = combined.processed_dataframe.iloc[:ref_n]["fluo"].unique()
    mov_fluo = combined.processed_dataframe.iloc[ref_n:]["fluo"].unique()
    assert len(ref_fluo) == 1 and len(mov_fluo) == 1
    assert ref_fluo[0] != mov_fluo[0], (
        "Reference and moving halves must be assigned distinct fluorophore IDs"
    )


def test_combine_datasets_tim_ordering(npy_path):
    """Moving dataset tim values exceed the reference maximum before and after combining."""
    ref_mbm_data = _make_mbm_data(_BEAD_POSITIONS_ZYX, bead_names=_BEAD_NAMES)
    mov_mbm_data = _make_mbm_data(_BEAD_POSITIONS_ZYX, bead_names=_BEAD_NAMES)

    ref_ds = _make_dataset(npy_path, tim_offset=0.0, mbm_data=ref_mbm_data)
    tim_max_ref = ref_ds.processed_dataframe["tim"].max()
    tim_offset_for_moving = tim_max_ref + 1.0

    mov_ds = _make_dataset(
        npy_path, tim_offset=tim_offset_for_moving, mbm_data=mov_mbm_data
    )

    assert mov_ds.processed_dataframe["tim"].min() > tim_max_ref, (
        "Moving dataset must have tim values strictly greater than the reference maximum"
    )

    combined = combine_datasets_with_bead_alignment(ref_ds, mov_ds)
    assert combined is not None

    ref_n = len(ref_ds.processed_dataframe)
    tim_ref_half = combined.processed_dataframe.iloc[:ref_n]["tim"]
    tim_mov_half = combined.processed_dataframe.iloc[ref_n:]["tim"]
    assert tim_mov_half.min() > tim_ref_half.max(), (
        "All moving tim values must remain above all reference tim values after combining"
    )


def test_combine_datasets_no_mbm_data_reference(npy_path):
    """Missing mbm_data on the reference dataset → combine returns None."""
    mov_mbm_data = _make_mbm_data(_BEAD_POSITIONS_ZYX, bead_names=_BEAD_NAMES)

    ref_ds = _make_dataset(npy_path, mbm_data=None)
    mov_ds = _make_dataset(npy_path, mbm_data=mov_mbm_data)

    assert combine_datasets_with_bead_alignment(ref_ds, mov_ds) is None


def test_combine_datasets_no_mbm_data_moving(npy_path):
    """Missing mbm_data on the moving dataset → combine returns None."""
    ref_mbm_data = _make_mbm_data(_BEAD_POSITIONS_ZYX, bead_names=_BEAD_NAMES)

    ref_ds = _make_dataset(npy_path, mbm_data=ref_mbm_data)
    mov_ds = _make_dataset(npy_path, mbm_data=None)

    assert combine_datasets_with_bead_alignment(ref_ds, mov_ds) is None


def test_combine_datasets_no_common_beads(npy_path):
    """No bead names in common → alignment fails → combine returns None."""
    ref_mbm_data = _make_mbm_data(
        _BEAD_POSITIONS_ZYX, bead_names=["ref_A", "ref_B", "ref_C"]
    )
    mov_mbm_data = _make_mbm_data(
        _BEAD_POSITIONS_ZYX, bead_names=["mov_A", "mov_B", "mov_C"]
    )

    ref_ds = _make_dataset(npy_path, mbm_data=ref_mbm_data)
    mov_ds = _make_dataset(npy_path, mbm_data=mov_mbm_data)

    assert combine_datasets_with_bead_alignment(ref_ds, mov_ds) is None
