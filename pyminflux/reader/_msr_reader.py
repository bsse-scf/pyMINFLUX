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
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, fields
from pathlib import Path
from pprint import pprint
from typing import BinaryIO, NewType, Union

# Some type aliases to make the code easier to understand
int32 = NewType("int32", int)
uint32 = NewType("uint32", int)
int64 = NewType("int64", int)
uint64 = NewType("uint64", int)


@dataclass
class BaseDataclass:
    """Do not instantiate this class directly."""

    def __setattr__(self, key, value):
        # Check if the attribute already exists
        if key in {f.name for f in fields(self)}:
            super().__setattr__(key, value)
        else:
            raise AttributeError(
                f"Cannot add new attribute '{key}' to {self.__class__.__name__}"
            )


@dataclass
class SIFraction(BaseDataclass):
    numerator: int32
    denominator: int32


@dataclass
class SIUnit(BaseDataclass):
    exponents: list[SIFraction]
    scale_factor: float


@dataclass
class OBSFileHeader(BaseDataclass):
    magic_header: bytes = (b"",)  # It should be: b"OMAS_BF\n\xff\xff"
    format_version: uint32 = 0  # Format version >= 2 supported
    first_stack_pos: uint64 = 0
    descr_len: uint32 = 0
    description: str = ""
    meta_data_position: uint32 = 0


@dataclass
class OBSFileMetadata(BaseDataclass):
    tree: ET = None
    unknown_strings: list[str] = field(default_factory=list)


@dataclass
class OFBStackMetadata(BaseDataclass):
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
    variable_metadata_start_position: uint64 = 0
    footer_start_pos: uint64 = 0

    # Version 1
    footer_size: uint32 = 0
    has_col_positions: list[uint32] = field(default_factory=list)
    has_col_labels: list[bool] = field(default_factory=list)

    # Version 1A
    obsolete_metadata_length: uint32 = 0

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

    #
    # After footer
    #
    labels: list[str] = field(default_factory=list)
    steps: list[float] = field(default_factory=list)
    flush_points: list[uint64] = field(default_factory=list)
    chunk_logical_positions: list[uint64] = field(default_factory=list)
    chunk_file_positions: list[uint64] = field(default_factory=list)
    tag_dictionary: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Constants:
    BF_MAX_DIMENSIONS: int = 15
    OBF_SI_FRACTION_SIZE: int = 8
    OBF_SI_FRACTION_NUM_ELEMENTS: int = 9
    OBF_SI_UNIT_SIZE: int = OBF_SI_FRACTION_NUM_ELEMENTS * OBF_SI_FRACTION_SIZE + 8

    VERSION_1_FOOTER_LENGTH: int = 124
    VERSION_1A_FOOTER_LENGTH: int = 128
    VERSION_2_FOOTER_LENGTH: int = 1408
    VERSION_3_FOOTER_LENGTH: int = 1424
    VERSION_4_FOOTER_LENGTH: int = 1432
    VERSION_5_FOOTER_LENGTH: int = 1444
    VERSION_5A_FOOTER_LENGTH: int = 1452
    VERSION_6_FOOTER_LENGTH: int = 1468
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

        # Metadata
        self.metadata = OBSFileMetadata()

        # Stack metadata (OBF_STACK_HEADERS + OBF_STACK_FOOTERS + plus additional info)
        self.obf_stacks_list: list[OFBStackMetadata] = []

    def scan(self) -> bool:
        """Scan the metadata of the file."""

        # Open the file
        with open(self.filename, mode="rb") as f:

            if not self._read_obf_header(f):
                return False

            # Scan metadata
            self.metadata = self._scan_metadata(f, self.obf_file_header)

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
            else f.read(obf_stack_metadata.length_stack_description).decode("utf-8")
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

    def _read_obf_stack_footer(self, f: BinaryIO, obf_stack_metadata: OFBStackMetadata):
        """Process footer."""

        #
        # Version 0
        #

        # Current position (beginning of the footer)
        obf_stack_metadata.footer_start_pos = f.tell()

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

        # Position of the beginning of the variable metadata
        obf_stack_metadata.variable_metadata_start_position = (
            obf_stack_metadata.footer_start_pos + obf_stack_metadata.footer_size
        )

        # Entries are != 0 for all axes that have a pixel position array (after the footer)
        col_positions_present = []
        for i in range(Constants.BF_MAX_DIMENSIONS):
            p = struct.unpack("<I", f.read(4))[0]
            if i < obf_stack_metadata.rank:
                col_positions_present.append(p != 0)
            current_size += 4
        obf_stack_metadata.has_col_positions = col_positions_present

        # Entries are != 0 for all axes that have a label (after the footer)
        col_labels_present = []
        for i in range(Constants.BF_MAX_DIMENSIONS):
            b = struct.unpack("<I", f.read(4))[0]
            if i < obf_stack_metadata.rank:
                col_labels_present.append(b != 0)
            current_size += 4
        obf_stack_metadata.has_col_labels = col_labels_present

        # Metadata length (superseded by tag dictionary in version > 4)
        obf_stack_metadata.obsolete_metadata_length = struct.unpack("<I", f.read(4))[0]
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

        # Min supported format version
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

        #
        # Read data after the end of footer
        #

        f.seek(obf_stack_metadata.variable_metadata_start_position)

        # Read labels
        labels = []
        for i in range(obf_stack_metadata.rank):
            n = struct.unpack("<I", f.read(4))[0]
            label = f.read(n).decode("utf-8")
            labels.append(label)
        obf_stack_metadata.labels = labels

        # Read steps (where presents)
        steps = []
        for dimension in range(obf_stack_metadata.rank):
            lst = []
            if obf_stack_metadata.has_col_positions[dimension]:
                for position in range(obf_stack_metadata.num_pixels[dimension]):
                    step = struct.unpack("<d", f.read(8))[0]
                    lst.append(step)
            steps.append(lst)

        # Skip the obsolete metadata
        f.seek(f.tell() + obf_stack_metadata.obsolete_metadata_length)

        # Flush points
        if obf_stack_metadata.num_flush_points > 0:
            flush_points = []
            for i in range(obf_stack_metadata.num_flush_points):
                flush_points.append(struct.unpack("<Q", f.read(8))[0])
            obf_stack_metadata.flush_points = flush_points

        # Tag dictionary
        tag_dictionary = {}
        length_key = 1
        while length_key > 0:
            new_key = self._read_string(f)
            length_key = len(new_key)
            if length_key > 0:
                new_value = self._read_string(f)
                # if new_key in ["imspector", "minflux"]:
                #     try:
                #         new_value = ET.fromstring(new_value)
                #     except ET.ParseError:
                #         pass
                tag_dictionary[new_key] = new_value
        obf_stack_metadata.tag_dictionary = tag_dictionary

        # Chunk positions
        if obf_stack_metadata.num_chunk_positions > 0:
            logical_positions = []
            file_positions = []

            # Start with 0
            logical_positions.append(0)
            file_positions.append(0)

            for i in range(obf_stack_metadata.num_chunk_positions):
                logical_positions.append(struct.unpack("<Q", f.read(8))[0])
                file_positions.append(struct.unpack("<Q", f.read(8))[0])

            obf_stack_metadata.chunk_logical_positions = logical_positions
            obf_stack_metadata.chunk_file_positions = file_positions

        # Return
        return obf_stack_metadata

    def _scan_metadata(self, f: BinaryIO, obf_file_header: OBSFileHeader):
        """Scan the metadata at the location stored in the header.

        The expected values are a key matching: "ome_xml" followed by
        valid OME XML metadata that we parse and return as an ElementTree.
        """

        if obf_file_header.meta_data_position == 0:
            return None

        # Remember current position
        current_pos = f.tell()

        # Move to the beginning of the metadata
        f.seek(obf_file_header.meta_data_position)

        # Initialize OBSFileMetadata object
        metadata = OBSFileMetadata()

        # Keep reading strings until done
        strings = []
        length_str = 1
        while length_str > 0:
            new_str = self._read_string(f)
            length_str = len(new_str)
            if length_str > 0:
                strings.append(new_str)

        # Now parse
        success = False
        tree = None
        if len(strings) == 2 and strings[0] == "ome_xml":
            try:
                tree = ET.fromstring(strings[1])
                success = True
            except ET.ParseError as e:
                success = False

        if not success:
            metadata.tree = None
            metadata.unknown_strings = strings
        else:
            metadata.tree = tree
            metadata.unknown_strings = []

        # Return to previous file position
        f.seek(current_pos)

        return metadata

    @staticmethod
    def _read_string(f: BinaryIO, as_str: bool = True) -> Union[str, bytes]:
        """Read a string at current position."""

        # Read the length of the following string
        length = struct.unpack("<I", f.read(4))[0]
        if length == 0:
            return ""

        # Read `length` bytes and convert them to utf-8 if requested
        value = f.read(length)
        if as_str:
            value = value.decode("utf-8")

        return value

    def print_stack_headers(self):
        """Print extracted stack headers."""
        for i, header in enumerate(self.obf_stacks_list):
            print(f"Stack {i:3}:"), pprint(header)
