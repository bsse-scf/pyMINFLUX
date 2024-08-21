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
#  limitations under the License.
import struct
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pprint
from typing import BinaryIO, NewType, Union

# Some type aliases to make the code easier to understand
int32 = NewType("int32", int)
uint32 = NewType("uint32", int)
int64 = NewType("int64", int)
uint64 = NewType("uint64", int)


@dataclass
class SIFraction:
    numerator: int32
    denominator: int32


@dataclass
class SIUnit:
    exponents: list[SIFraction]
    scale_factor: float


@dataclass
class OBSFileHeader:
    magic_header: bytes = (b"",)  # It should be: b"OMAS_BF\n\xff\xff"
    format_version: uint32 = 0  # Format version >= 2 supported
    first_stack_pos: uint64 = 0
    descr_len: uint32 = -1
    description: str = ""
    meta_data_position: uint32 = 0


@dataclass
class OFBStackMetadata:
    #
    # Header
    #
    magic_header: bytes = b""  # It should be: b"OMAS_BF_STACK\n\xff\xff"
    format_version: uint32 = 0
    rank: uint32 = 0
    num_pixels: list[uint32] = field(
        default_factory=list
    )  # "res" in the original documentation
    physical_lengths: list[float] = field(
        default_factory=list
    )  # "len" in the original documentation
    physical_offsets: list[float] = field(
        default_factory=list
    )  # "off" in the original documentation
    data_type_on_disk: uint32 = 0  # "dt" in the original documentation
    compression_type: uint32 = 0
    compression_level: uint32 = 0
    length_stack_name: uint32 = 0  # Length of the stack name in bytes (-> utf-8)
    length_stack_description: uint32 = (
        0  # Length of the stack description in bytes (-> utf-8 -> xml)
    )
    reserved: uint64 = 0  # Do not touch
    data_len_disk: uint64 = (
        0  # Length of data on disk; version 6: offset from the end of the header + description to the stack footer
    )
    next_stack_pos: uint64 = (0,)
    stack_name: str = ""
    stack_description: str = ""
    data_position: uint64 = 0

    #
    # Footer
    #

    # Custom
    start_position: uint64 = 0

    # Version 1
    footer_size: uint32 = 0
    has_col_positions: list[uint32] = field(default_factory=list)
    has_col_labels: list[uint32] = field(default_factory=list)
    has_row_labels: list[uint32] = field(default_factory=list)

    # Version 1A
    metadata_length: uint32 = 0

    # Version 2
    si_value: SIUnit = None
    si_dimensions: list[SIUnit] = field(default_factory=list)

    # Version 3
    num_flush_points: uint64 = 0
    flush_block_size: uint64 = 0

    # Version 4
    tag_dictionary_length: uint64 = 0

    # Version 5
    stack_end_disk: uint64 = 0
    min_format_version: uint32 = 0
    stack_end_used_disk: uint64 = 0

    # Version 6
    samples_written: uint64 = 0
    num_chunk_positions: uint64 = 0

    # Version 7: nothing


@dataclass(frozen=True)
class Constants:
    BF_MAX_DIMENSIONS: int = 15
    OBF_SI_FRACTION_SIZE: int = 8
    OBF_SI_FRACTION_NUM_ELEMENTS: int = 9
    OBF_SI_UNIT_SIZE: int = OBF_SI_FRACTION_NUM_ELEMENTS * OBF_SI_FRACTION_SIZE + 8

    VERSION_1_FOOTER_LENGTH: int = (
        4 + 4 * BF_MAX_DIMENSIONS + 4 * BF_MAX_DIMENSIONS
    )  # 124
    VERSION_1A_FOOTER_LENGTH: int = VERSION_1_FOOTER_LENGTH + 4  # 128
    VERSION_2_FOOTER_LENGTH: int = (
        VERSION_1A_FOOTER_LENGTH
        + OBF_SI_UNIT_SIZE
        + OBF_SI_UNIT_SIZE * BF_MAX_DIMENSIONS
    )  # 1408
    VERSION_3_FOOTER_LENGTH: int = VERSION_2_FOOTER_LENGTH + 8 + 8  # 1424
    VERSION_4_FOOTER_LENGTH: int = VERSION_3_FOOTER_LENGTH + 8  # 1432
    VERSION_5_FOOTER_LENGTH: int = VERSION_4_FOOTER_LENGTH + 8 + 4  # 1444
    VERSION_5A_FOOTER_LENGTH: int = VERSION_5_FOOTER_LENGTH + 8  # 1452
    VERSION_6_FOOTER_LENGTH: int = VERSION_5A_FOOTER_LENGTH + 8 + 8  # 1468
    VERSION_7_FOOTER_LENGTH: int = 1528  # No documentation on what is new


def get_footer_struct_size(version) -> int:
    if version == 0:
        return 0
    elif version == 1:
        return Constants.VERSION_1A_FOOTER_LENGTH  # We return version "1A"
    elif version == 2:
        return Constants.VERSION_2_FOOTER_LENGTH
    elif version == 3:
        return Constants.VERSION_3_FOOTER_LENGTH
    elif version == 4:
        return Constants.VERSION_4_FOOTER_LENGTH
    elif version == 5:
        return Constants.VERSION_5A_FOOTER_LENGTH  # We return version "5A"
    elif version == 6:
        return Constants.VERSION_6_FOOTER_LENGTH
    elif version == 7:
        return Constants.VERSION_7_FOOTER_LENGTH
    else:
        raise ValueError(f"Unexpected stack version {version}.")


class MSRReader:
    """Reads data and metadata information from `.MSR` (OBF format) files.

    For documentation, see:
    https://imspectordocs.readthedocs.io/en/latest/fileformat.html#the-obf-file-format

    Note: binary data is stored in little-endian order.
    """

    def __init__(self, filename: Union[Path, str]):
        """Constructor.

        Parameters
        ----------
        filename: Union[Path, str]
            Full path to the file name to open.
        """

        # Store the filename
        self.filename = Path(filename)

        # OBF_FILE_HEADER structure
        self.obf_file_header = OBSFileHeader()

        # Stack metadata (OBF_STACK_HEADERS + OBF_STACK_FOOTERS + plus additional info)
        self.obf_stacks_list: list[OFBStackMetadata] = []

    def scan(self) -> bool:
        """Scan the metadata of the file."""

        # Open the file
        with open(self.filename, mode="rb") as f:

            if not self._read_obf_header(f):
                return False

            # Get the first stack position
            next_stack_pos = self.obf_file_header.first_stack_pos

            while next_stack_pos != 0:

                # Scan the next stack
                success, obs_stack_metadata = self._read_obf_stack(f, next_stack_pos)

                if not success:
                    return False

                # Append current stack header
                self.obf_stacks_list.append(obs_stack_metadata)

                # Do we have a next header to parse?
                next_stack_pos = obs_stack_metadata.next_stack_pos

        return True

    def _read_obf_header(self, f) -> bool:
        """Read the OBF header."""

        # Read the magic header
        magic_header = f.read(10)

        if not magic_header == b"OMAS_BF\n\xff\xff":
            print("Not a valid MSR (OBF) file.")
            return False

        # Store the magic header
        self.obf_file_header.magic_header = magic_header

        # Get format version (uint32)
        self.obf_file_header.format_version = struct.unpack("<I", f.read(4))[0]

        if self.obf_file_header.format_version < 2:
            print("The MSR (OBF) file must be version 2 or above.")
            return False

        # Get position of the first stack header in the file (uint64)
        self.obf_file_header.first_stack_pos = struct.unpack("<Q", f.read(8))[0]

        # Get length of following utf-8 description (uint32)
        self.obf_file_header.descr_len = struct.unpack("<I", f.read(4))[0]

        # Get description (bytes -> utf-8)
        description = ""
        if self.obf_file_header.descr_len > 0:
            description = f.read(self.obf_file_header.descr_len).decode(
                "utf-8", errors="replace"
            )
        self.obf_file_header.description = description

        # Get metadata position (uint64)
        self.obf_file_header.meta_data_position = struct.unpack("<Q", f.read(8))[0]

        return True

    def _read_obf_stack(
        self, f: BinaryIO, next_stack_pos: int
    ) -> tuple[bool, OFBStackMetadata]:
        """Read current OBF stack metadata (header + footer)."""

        # Initialize the metadata
        obf_stack_metadata = OFBStackMetadata()

        # Move at the beginning of the stack
        f.seek(next_stack_pos)

        # Read the header
        success, obf_stack_metadata = self._read_obf_stack_header(f, obf_stack_metadata)
        if not success:
            return False, obf_stack_metadata

        # Process the footer
        obf_stack_metadata = self._read_obf_stack_footer(f, obf_stack_metadata)

        # Return
        return True, obf_stack_metadata

    def _read_obf_stack_header(
        self, f: BinaryIO, obf_stack_metadata: OFBStackMetadata
    ) -> tuple[bool, OFBStackMetadata]:
        """Read the OBF stack header and update metadata.

        The file should already be positioned at the right location.

        Parameters
        ----------

        f: BinaryIO
            File handle to open.

        obf_stack_metadata: OFBStackMetadata
            Current OFBStackMetadata object

        Returns
        -------

        success: bool
            Whether parsing was successful.

        obf_stack_metadata: OFBStackMetadata
            Updated OFBStackMetadata object
        """

        # # Initialize the metadata
        # obf_stack_metadata = OFBStackMetadata()

        #
        # Parse the header
        #

        # # Move to position pos
        # f.seek(next_stack_pos)

        # Read the magic header
        obf_stack_metadata.magic_header = f.read(16)

        if not obf_stack_metadata.magic_header == b"OMAS_BF_STACK\n\xff\xff":
            print("Could not find OBF stack header.")
            return False, obf_stack_metadata

        # Get format version (uint32)
        obf_stack_metadata.format_version = struct.unpack("<I", f.read(4))[0]

        # Get the number of valid dimensions
        obf_stack_metadata.rank = struct.unpack("<I", f.read(4))[0]

        # Get the number of pixels along each dimension
        obf_stack_metadata.num_pixels = []
        for i in range(Constants.BF_MAX_DIMENSIONS):
            n = struct.unpack("<I", f.read(4))[0]
            if i < obf_stack_metadata.rank:
                obf_stack_metadata.num_pixels.append(n)

        # Get the physical lengths along each dimension
        obf_stack_metadata.physical_lengths = []
        for i in range(Constants.BF_MAX_DIMENSIONS):
            p = struct.unpack("<d", f.read(8))[0]
            if i < obf_stack_metadata.rank:
                obf_stack_metadata.physical_lengths.append(p)

        # Get the physical lengths along each dimension
        obf_stack_metadata.physical_offsets = []
        for i in range(Constants.BF_MAX_DIMENSIONS):
            o = struct.unpack("<d", f.read(8))[0]
            if i < obf_stack_metadata.rank:
                obf_stack_metadata.physical_offsets.append(o)

        # Read the data type; it should be one of:
        # 0x00000000: automatically determine the data type
        # 0x00000001: uint8
        # 0x00000002: int8
        # 0x00000004: uint16
        # 0x00000008: int16
        # 0x00000010: uint32
        # 0x00000020: int32
        # 0x00000040: float32
        # 0x00000080: float64 (double)
        # 0x00000400: Byte RGB, 3 samples per pixel
        # 0x00000800: Byte RGB, 4 samples per pixel
        # 0x00001000: uint64
        # 0x00002000: int64
        # 0x00010000: (c++) boolean
        #
        # Note: all numeric formats have a complex-number variant with
        # format: data_type | 0x40000000
        obf_stack_metadata.data_type_on_disk = struct.unpack("<I", f.read(4))[0]

        # Compression type (0 for none, 1 for zip)
        obf_stack_metadata.compression_type = struct.unpack("<I", f.read(4))[0]

        # Compression level (0 through 9)
        obf_stack_metadata.compression_level = struct.unpack("<I", f.read(4))[0]

        # Length of the stack name
        obf_stack_metadata.length_stack_name = struct.unpack("<I", f.read(4))[0]

        # Description length
        obf_stack_metadata.length_stack_description = struct.unpack("<I", f.read(4))[0]

        # Reserved field
        obf_stack_metadata.reserved = struct.unpack("<Q", f.read(8))[0]

        # Data length on disk
        obf_stack_metadata.data_len_disk = struct.unpack("<Q", f.read(8))[0]

        # Next stack position in the file
        obf_stack_metadata.next_stack_pos = struct.unpack("<Q", f.read(8))[0]

        # Scan also stack name and description (right after the end of the header)
        obf_stack_metadata.stack_name = (
            ""
            if obf_stack_metadata.length_stack_name == 0
            else f.read(obf_stack_metadata.length_stack_name).decode(
                "utf-8", errors="replace"
            )
        )
        obf_stack_metadata.stack_description = (
            ""
            if obf_stack_metadata.length_stack_description == 0
            else f.read(obf_stack_metadata.length_stack_description).decode(
                "utf-8", errors="replace"
            )
        )

        # Now we are at the beginning of the data
        obf_stack_metadata.data_position = f.tell()

        # Start position of the footer
        footer_start_position = (
            obf_stack_metadata.data_position + obf_stack_metadata.data_len_disk
        )

        # Move to the beginning of the footer
        f.seek(footer_start_position)

        return True, obf_stack_metadata

    def print_stack_headers(self):
        """Print extracted stack headers."""
        for i, header in enumerate(self.obf_stacks_list):
            print(f"Stack {i:3}:"), pprint(header)

    def _read_obf_stack_footer(self, f: BinaryIO, obf_stack_metadata: OFBStackMetadata):
        """Process footer."""

        #
        # Version 0
        #

        # If stack version is 0, there is no footer
        if obf_stack_metadata.format_version == 0:
            obf_stack_metadata.footer_size = 0
            return obf_stack_metadata

        #
        # Version 1/1A
        #

        # What is the expected size of the footer for this header version?
        size_for_version = get_footer_struct_size(obf_stack_metadata.format_version)

        # Keep track ot the side while we proceed
        current_size = 0

        # Get size of the footer header
        obf_stack_metadata.footer_size = struct.unpack("<I", f.read(4))[0]
        current_size += 4

        # Entries are != 0 for all axes that have a pixel position array (after the footer)
        col_positions = []
        for i in range(Constants.BF_MAX_DIMENSIONS):
            p = struct.unpack("<I", f.read(4))[0]
            col_positions.append(p)
            current_size += 4
        obf_stack_metadata.has_col_positions = col_positions

        # Entries are != 0 for all axes that have a label (after the footer)
        col_labels = []
        for i in range(Constants.BF_MAX_DIMENSIONS):
            b = struct.unpack("<I", f.read(4))[0]
            col_labels.append(b)
            current_size += 4
        obf_stack_metadata.has_col_labels = col_labels

        # Metadata length (superseded by tag dictionary in version > 4)
        obf_stack_metadata.metadata_length = struct.unpack("<I", f.read(4))[0]
        current_size += 4

        # Internal check
        assert (
            current_size == Constants.VERSION_1A_FOOTER_LENGTH
        ), "Unexpected length of version 1/1A data."

        # Have we read enough for this version?
        if current_size > size_for_version:
            return obf_stack_metadata

        #
        # Version 2
        #

        # SI units of the value carried
        fractions = []
        for i in range(Constants.OBF_SI_FRACTION_NUM_ELEMENTS):
            numerator = struct.unpack("<i", f.read(4))[0]
            denominator = struct.unpack("<i", f.read(4))[0]
            fractions.append(SIFraction(numerator=numerator, denominator=denominator))
            current_size += 8
        scale_factor = struct.unpack("<d", f.read(8))[0]
        current_size += 8
        si_value = SIUnit(exponents=fractions, scale_factor=scale_factor)
        obf_stack_metadata.si_value = si_value

        # SI units of the axes
        dimensions = []
        for i in range(Constants.BF_MAX_DIMENSIONS):
            fractions = []
            for j in range(Constants.OBF_SI_FRACTION_NUM_ELEMENTS):
                numerator = struct.unpack("<i", f.read(4))[0]
                denominator = struct.unpack("<i", f.read(4))[0]
                fractions.append(
                    SIFraction(numerator=numerator, denominator=denominator)
                )
                current_size += 8
            scale_factor = struct.unpack("<d", f.read(8))[0]
            current_size += 8
            dimensions.append(SIUnit(exponents=fractions, scale_factor=scale_factor))

        # Add all SI dimensions
        obf_stack_metadata.si_dimensions = dimensions

        # Internal check
        assert (
            current_size == Constants.VERSION_2_FOOTER_LENGTH
        ), "Unexpected length of version 2 data."

        # Have we read enough for this version?
        if current_size > size_for_version:
            return obf_stack_metadata

        #
        # Version 3
        #

        # The number of flush points
        num_flush_points = struct.unpack("<Q", f.read(8))[0]
        current_size += 8
        obf_stack_metadata.num_flush_points = num_flush_points

        # The flush block size
        flush_block_size = struct.unpack("<Q", f.read(8))[0]
        current_size += 8
        obf_stack_metadata.flush_block_size = flush_block_size

        # Internal check
        assert (
            current_size == Constants.VERSION_3_FOOTER_LENGTH
        ), "Unexpected length of version 3 data."

        # Have we read enough for this version?
        if current_size > size_for_version:
            return obf_stack_metadata

        #
        # Version 4
        #
        obf_stack_metadata.tag_dictionary_length = struct.unpack("<Q", f.read(8))[0]
        current_size += 8

        # Internal check
        assert (
            current_size == Constants.VERSION_4_FOOTER_LENGTH
        ), "Unexpected length of version 4 data."

        # Have we read enough for this version?
        if current_size > size_for_version:
            return obf_stack_metadata

        #
        # Version 5/5A
        #

        # Where on disk all the meta-data ends
        obf_stack_metadata.stack_end_disk = struct.unpack("<Q", f.read(8))[0]
        current_size += 8

        # Min supported format version: should always be 1
        obf_stack_metadata.min_format_version = struct.unpack("<I", f.read(4))[0]
        current_size += 4

        # The position where the stack ends on disk.
        obf_stack_metadata.stack_end_used_disk = struct.unpack("<Q", f.read(8))[0]
        current_size += 8

        # Internal check
        assert (
            current_size == Constants.VERSION_5A_FOOTER_LENGTH
        ), "Unexpected length of version 5/5A data."

        # Have we read enough for this version?
        if current_size > size_for_version:
            return obf_stack_metadata

        #
        # Version 6
        #

        # The total number of samples available on disk. By convention all remaining data is
        # assumed to be zero or undefined. If this is less than the data contained of the stack
        # it is safe to assume that the stack was truncated by ending the measurement early.
        # If 0, the number of samples written is the one expected from the stack size.
        obf_stack_metadata.samples_written = struct.unpack("<Q", f.read(8))[0]
        current_size += 8

        obf_stack_metadata.num_chunk_positions = struct.unpack("<Q", f.read(8))[0]
        current_size += 8

        # Internal check
        assert (
            current_size == Constants.VERSION_6_FOOTER_LENGTH
        ), "Unexpected length of version 6 data."

        # Have we read enough for this version?
        if current_size > size_for_version:
            return obf_stack_metadata

        #
        # Version 7
        #

        # There is no new documented footer metadata for version 7.

        # Return
        return obf_stack_metadata
