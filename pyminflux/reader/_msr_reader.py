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
import json
import re
import struct
import xml.etree.ElementTree as ET
import zlib
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import BinaryIO, NewType, Union

import numpy as np
from natsort import natsorted

# Some type aliases to make the code easier to understand
int32 = NewType("int32", int)
uint32 = NewType("uint32", int)
int64 = NewType("int64", int)
uint64 = NewType("uint64", int)


@dataclass
class _BaseDataclass:
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
class SIFraction(_BaseDataclass):
    """A fraction, composed of a numerator and a denominator."""

    numerator: int32
    denominator: int32


@dataclass
class SIUnit(_BaseDataclass):
    """The dimensions and scaling factor of an SI unit. For each of the
     base and supplemental units the exponent is saved as a fraction.

    Ordering for the exponents array is as follows:
    exponents[0]: Meters (M)
    exponents[1]: Kilograms (KG)
    exponents[2]: Seconds (S)
    exponents[3]: Amperes (A)
    exponents[4]: Kelvin (K)
    exponents[5]: Moles (MOL)
    exponents[6]: Candela (CD)
    exponents[7]: Radian (R)
    exponents[8]: Steradian (SR)
    """

    exponents: list[SIFraction]
    scale_factor: float


@dataclass
class OBFFileHeader(_BaseDataclass):
    """File binary header."""

    magic_header: bytes = (b"",)  # It should be: b"OMAS_BF\n\xff\xff"
    format_version: uint32 = 0  # Format version >= 2 supported
    first_stack_pos: uint64 = 0
    descr_len: uint32 = 0
    description: str = ""
    meta_data_position: uint32 = 0


@dataclass
class OBFFileMetadata(_BaseDataclass):
    """File OME-XML metadata."""

    tree: ET = None
    unknown_strings: list[str] = field(default_factory=list)


@dataclass
class OBFStackMetadata(_BaseDataclass):
    """OBF Stack metadata."""

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
    data_start_position: uint64 = 0

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
    bytes_per_sample: int = 0


@dataclass(frozen=True)
class _Constants:
    """_Constants."""

    BF_MAX_DIMENSIONS: int = 15
    OBF_SI_FRACTION_SIZE: int = 8
    OBF_SI_FRACTION_NUM_ELEMENTS: int = 9
    OBF_SI_UNIT_SIZE: int = OBF_SI_FRACTION_NUM_ELEMENTS * OBF_SI_FRACTION_SIZE + 8

    V1_FOOTER_LENGTH: int = 124
    V1A_FOOTER_LENGTH: int = 128
    V2_FOOTER_LENGTH: int = 1408
    V3_FOOTER_LENGTH: int = 1424
    V4_FOOTER_LENGTH: int = 1432
    V5_FOOTER_LENGTH: int = 1444
    V5A_FOOTER_LENGTH: int = 1452
    V6_FOOTER_LENGTH: int = 1468
    V7_FOOTER_LENGTH: int = 1528  # No documentation on what is new


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

        # File header
        self.obf_file_header = OBFFileHeader()

        # Metadata
        self.obf_file_metadata = OBFFileMetadata()

        # List of stack metadata objects
        self._obf_stacks_list: list[OBFStackMetadata] = []

    def scan(self) -> bool:
        """Scan the metadata of the file.

        Returns
        -------

        success: bool
            True if the file was scanned successfully, False otherwise.
        """

        # Open the file
        with open(self.filename, mode="rb") as f:

            if not self._read_obf_header(f):
                return False

            # Scan metadata
            self.obf_file_metadata = self._scan_metadata(f, self.obf_file_header)

            # Get the first stack position
            next_stack_pos = self.obf_file_header.first_stack_pos

            while next_stack_pos != 0:

                # Scan the next stack
                success, obs_stack_metadata = self._read_obf_stack(f, next_stack_pos)

                if not success:
                    return False

                # Append current stack header
                self._obf_stacks_list.append(obs_stack_metadata)

                # Do we have a next header to parse?
                next_stack_pos = obs_stack_metadata.next_stack_pos

        return True

    def __getitem__(self, stack_index: int) -> Union[OBFStackMetadata, None]:
        """Allows accessing the reader with the `[]` notation to get the next stack metadata.

        Parameters
        ----------

        stack_index: int
            Index of the stack to be retrieved.

        Returns
        -------

        metadata: Union[OBFStackMetadata, None]
            Metadata for the requested stack, or None if no file was loaded.
        """

        # Is anything loaded?
        if len(self._obf_stacks_list) == 0:
            return None

        if stack_index < 0 or stack_index > (len(self._obf_stacks_list) - 1):
            raise ValueError(f"Index value {stack_index} is out of bounds.")

        # Get and return the metadata
        metadata = self._obf_stacks_list[stack_index]
        return metadata

    def __iter__(self):
        """Return the iterator.

        Returns
        -------

            iterator
        """
        self._current_index = 0
        return self

    def __next__(self):
        if self._current_index < len(self._obf_stacks_list):
            metadata = self.__getitem__(self._current_index)
            self._current_index += 1
            return metadata
        else:
            raise StopIteration

    @property
    def num_stacks(self):
        """Return the number of stacks contained in the file."""
        return len(self._obf_stacks_list)

    def get_data_physical_sizes(
        self, stack_index: int, scaled: bool = True
    ) -> Union[list, None]:
        """Returns the (scaled) data physical size for the requested stack.

        Parameters
        ----------

        stack_index: int
            Index of the stack for which to read the data.

        scaled: bool
            If scaled is True, the physical sizes will be scaled by the corresponding scale factors
            as reported by MSRReader.get_data_units().

        Returns
        -------

        offsets: Union[list, None]
            Physical sizes for 2D images, None otherwise.
        """

        if stack_index < 0 or stack_index > len(self._obf_stacks_list):
            raise ValueError(f"stack_index={stack_index} is out of bounds.")

        # Get the metadata for the requested stack
        obf_stack_metadata = self._obf_stacks_list[stack_index]

        if obf_stack_metadata is None:
            return None

        # Get the physical lengths
        phys_lengths = obf_stack_metadata.physical_lengths[: obf_stack_metadata.rank]

        # Do we need to scale?
        if scaled:
            _, factors = self.get_data_units(stack_index=stack_index)
            for i, factor in enumerate(factors):
                if factor != 1.0:
                    phys_lengths[i] *= factor

        # Return the physical lengths as list
        return phys_lengths

    def get_data_offsets(
        self, stack_index: int, scaled: bool = True
    ) -> Union[list, None]:
        """Returns the (scaled) data offsets for the requested stack.

        Parameters
        ----------

        stack_index: int
            Index of the stack for which to read the data.

        scaled: bool
            If scaled is True, the offsets will be scaled by the corresponding scale factors
            as reported by MSRReader.get_data_units().

        Returns
        -------

        offsets: Union[list, None]
            Offsets for 2D images, None otherwise.
        """

        if stack_index < 0 or stack_index > len(self._obf_stacks_list):
            raise ValueError(f"stack_index={stack_index} is out of bounds.")

        # Get the metadata for the requested stack
        obf_stack_metadata = self._obf_stacks_list[stack_index]

        if obf_stack_metadata is None:
            return None

        # Get the offsets
        offsets = obf_stack_metadata.physical_offsets[: obf_stack_metadata.rank]

        # Do we need to scale?
        if scaled:
            _, factors = self.get_data_units(stack_index=stack_index)
            for i, factor in enumerate(factors):
                if factor != 1.0:
                    offsets[i] *= factor

        return offsets

    def get_data_pixel_sizes(
        self, stack_index: int, scaled: bool = True
    ) -> Union[list, None]:
        """Returns the (scaled) data pixel size for the requested stack.

        Parameters
        ----------

        stack_index: int
            Index of the stack for which to read the data.

        scaled: bool
            If scaled is True, the pixel sizes will be scaled by the corresponding scale factors
            as reported by MSRReader.get_data_units().

        Returns
        -------

        offsets: Union[list, None]
            Pixel sizes for 2D images, None otherwise.
        """

        if stack_index < 0 or stack_index > len(self._obf_stacks_list):
            raise ValueError(f"stack_index={stack_index} is out of bounds.")

        # Get the metadata for the requested stack
        obf_stack_metadata = self._obf_stacks_list[stack_index]

        if obf_stack_metadata is None:
            return None

        # Get the physical sizes
        phys_lengths = self.get_data_physical_sizes(
            stack_index=stack_index, scaled=scaled
        )

        # Get the number of pixels along each dimension
        num_pixels = obf_stack_metadata.num_pixels[: obf_stack_metadata.rank]

        # Now divide by the image size
        pixel_sizes = np.array(phys_lengths) / np.array(num_pixels)

        # Return the pixel size as list
        return pixel_sizes.tolist()

    def get_data_units(self, stack_index: int) -> Union[tuple[list, list], None]:
        """Returns the data units and scale factors per dimension for requested stack.

        Units are one of:
            "m": meters
            "kg": kilograms
            "s": s
            "A": Amperes
            "K": Kelvin
            "mol": moles
            "cd": candela
            "r": radian
            "sr": sr

        Parameters
        ----------

        stack_index: int
            Index of the stack for which to read the data.

        Returns
        -------

        unit: Union[tuple[list, list], None]
            List of units and list of scale factors, or None if no file was opened.
        """

        if stack_index < 0 or stack_index > len(self._obf_stacks_list):
            raise ValueError(f"stack_index={stack_index} is out of bounds.")

        # Get the metadata for the requested stack
        obf_stack_metadata = self._obf_stacks_list[stack_index]

        if obf_stack_metadata is None:
            return None

        units = []
        scale_factors = []
        for dim in range(obf_stack_metadata.rank):
            dimensions = obf_stack_metadata.si_dimensions[dim]
            scale_factors.append(dimensions.scale_factor)
            for i, exponent in enumerate(dimensions.exponents):
                if i == 0 and exponent.numerator > 0:
                    units.append("m")
                    break
                elif i == 1 and exponent.numerator > 0:
                    units.append("kg")
                    break
                elif i == 2 and exponent.numerator > 0:
                    units.append("s")
                    break
                elif i == 3 and exponent.numerator > 0:
                    units.append("A")
                    break
                elif i == 4 and exponent.numerator > 0:
                    units.append("K")
                    break
                elif i == 5 and exponent.numerator > 0:
                    units.append("mol")
                    break
                elif i == 6 and exponent.numerator > 0:
                    units.append("cd")
                    break
                elif i == 7 and exponent.numerator > 0:
                    units.append("r")
                    break
                elif i == 8 and exponent.numerator > 0:
                    units.append("sr")
                    break
                else:
                    units.append("")
                    break

        # Return the extracted units and scale factors
        return units, scale_factors

    def get_data(self, stack_index: int) -> Union[np.ndarray, None]:
        """Read the data for requested stack: only images are returned.

        Parameters
        ----------

        stack_index: int
            Index of the stack for which to read the data.

        Returns
        -------

        frame: Union[np.ndarray, None]
            Data as a 2D NumPy array. None if it could not be read or if it was not a 2D image.
        """

        if stack_index < 0 or stack_index > len(self._obf_stacks_list):
            raise ValueError(f"stack_index={stack_index} is out of bounds.")

        # Get the metadata for the requested stack
        obf_stack_metadata = self._obf_stacks_list[stack_index]

        # Currently, we only support format 6 and newer
        if obf_stack_metadata.format_version < 6:
            print("Reading data is supported only for stack format 6 and newer.")
            return None

        # If there are chunks, we currently do not read
        if obf_stack_metadata.num_chunk_positions > 0:
            print("Reading chunked data is currently not supported.")
            return None

        # We currently only read 2D images
        if self._get_num_dims(obf_stack_metadata.num_pixels) != 2:
            print("Only 2D images are currently supported.")
            return None

        # Get NumPy data type
        np_data_type, _ = self._get_numpy_data_type(
            obf_stack_metadata.data_type_on_disk
        )
        if np_data_type is None:
            print("Unsupported data type.")
            return None

        # Extract some info
        height = obf_stack_metadata.num_pixels[1]
        width = obf_stack_metadata.num_pixels[0]
        bytes_per_sample = obf_stack_metadata.bytes_per_sample

        # Expected number of (decompressed) samples
        expected_num_samples = width * height

        # Number of written bytes
        written_bytes = obf_stack_metadata.samples_written * bytes_per_sample

        # Open the file
        with open(self.filename, mode="rb") as f:

            # Seek to the beginning of the data
            f.seek(obf_stack_metadata.data_start_position)

            # Is there compression?
            if obf_stack_metadata.compression_type != 0:

                # Read the bytes
                compressed_data = f.read(written_bytes)

                # Decompress them
                decompressed_data = zlib.decompress(compressed_data)

                # Cast to a "byte" NumPy array
                raw_frame = np.frombuffer(decompressed_data, dtype=np.uint8)

            else:

                # Read the bytes
                raw_data = f.read(written_bytes)

                # Cast to a "byte" NumPy array
                raw_frame = np.frombuffer(raw_data, dtype=np.uint8)

        # Reinterpret as final data type format (little Endian)
        frame = raw_frame.view(np.dtype(np_data_type))

        # Make sure the final frame size matches the expected size
        if len(frame) != expected_num_samples:
            print("Unexpected length of data retrieved!")
            return None

        # Reshape
        frame = frame.reshape((height, width))

        return frame

    def get_ome_xml_metadata(self) -> Union[str, None]:
        """Return the OME XML metadata.

        Returns
        -------

        ome_xml_metadata: Union[str, None]
            OME XML metadata as formatted string. If no file was loaded, returns None.
        """

        # Get the ome-xml tree
        root = self.obf_file_metadata.tree
        if root is None:
            return None

        # Return metadata as formatted XML string
        return self._tree_to_formatted_xml(root)

    def export_ome_xml_metadata(self, file_name: Union[str, Path]):
        """Export the OME-XML metadata to file.

        Parameters
        ----------

        file_name: Union[str, Path]
            Output file name.
        """

        # Get the ome-xml tree, optionally as formatted string
        metadata = self.get_ome_xml_metadata()
        if metadata is None:
            print("Nothing to export.")
            return

        # Make sure the parent path to the file exists
        Path(file_name).parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(metadata)

    def get_tag_dictionary(self, stack_index: int) -> Union[dict, None]:
        """Return the tag dictionary for the requested stack.

        Parameters
        ----------

        stack_index: int
            Index of the stack for which to return the tag dictionary.

        Returns
        -------

        tag_dictionary: Union[dict, None]
            Dictionary. If no file was loaded, returns None.
        """

        if stack_index < 0 or stack_index > len(self._obf_stacks_list):
            raise ValueError(f"Stack number {stack_index} is out of range.")

        # Get stack metadata
        obf_stack_metadata = self._obf_stacks_list[stack_index]
        if obf_stack_metadata is None:
            return None

        # Get the tag dictionary
        tag = obf_stack_metadata.tag_dictionary

        # Return the tag dictionary
        return tag

    def export_tag_dictionary(self, stack_index: int, file_name: Union[str, Path]):
        """Export the tag dictionary to file.

        Parameters
        ----------

        stack_index: int
            Index of the stack for which to export the tag dictionary.

        file_name: Union[str, Path]
            Output file name.
        """

        if stack_index < 0 or stack_index > len(self._obf_stacks_list):
            raise ValueError(f"Stack number {stack_index} is out of range.")

        # Get tag dictionary
        tag_dictionary = self.get_tag_dictionary(stack_index)
        if tag_dictionary is None:
            return None

        # Make sure file_name is of type Path
        file_name = Path(file_name)

        # Make sure the parent path to the file exists
        file_name.parent.mkdir(parents=True, exist_ok=True)

        # Export the dictionaries
        for key, value in tag_dictionary.items():
            if type(value) is ET.Element:
                mod_file_name = file_name.parent / f"{file_name.stem}_{key}.xml"
                xml_str = self._tree_to_formatted_xml(value)
                with open(mod_file_name, "w") as f:
                    f.write(xml_str)
            elif type(value) is dict:
                mod_file_name = file_name.parent / f"{file_name.stem}_{key}.json"
                with open(mod_file_name, "w") as f:
                    json.dump(value, f, indent=4)
            else:
                mod_file_name = file_name.parent / f"{file_name.stem}_{key}.txt"
                with open(mod_file_name, "w") as f:
                    f.write(value)

    @staticmethod
    def _tree_to_formatted_xml(root: ET, xml_declaration: bool = True) -> str:
        """Converts an xml. tree to formatted xml.

        Parameters
        ----------

        root: xml.etree.ElementTree
            Root element of the xml tree.

        xml_declaration: bool
            Whether to prepend the xml declaration to the converted xml.

        Returns
        -------

        xml_str: str
            Formatted xml.
        """

        # Format tree (optionally add xml declaration)
        xml_str = ET.tostring(
            root, encoding="utf-8", xml_declaration=xml_declaration, method="xml"
        ).decode("utf-8")

        # Remove tabs and new lines
        xml_str = re.sub(r"[\n\t]", "", xml_str)

        # Remove stretches of blank spaces between nodes
        xml_str = re.sub(r">\s+<", "><", xml_str)

        return xml_str

    @staticmethod
    def _get_footer_struct_size(version: int) -> int:
        """Returns the size in pixel of the footer structure for given version.

        Parameters
        ----------

        version: int
            Version number.

        Returns
        -------

        size: int
            Size in bytes of the footer structure for specified version.
        """
        if version == 0:
            return 0
        elif version == 1:
            return _Constants.V1A_FOOTER_LENGTH  # We return version "1A"
        elif version == 2:
            return _Constants.V2_FOOTER_LENGTH
        elif version == 3:
            return _Constants.V3_FOOTER_LENGTH
        elif version == 4:
            return _Constants.V4_FOOTER_LENGTH
        elif version == 5:
            return _Constants.V5A_FOOTER_LENGTH  # We return version "5A"
        elif version == 6:
            return _Constants.V6_FOOTER_LENGTH
        elif version == 7:
            return _Constants.V7_FOOTER_LENGTH
        else:
            raise ValueError(f"Unexpected stack version {version}.")

    @staticmethod
    def _get_num_dims(num_pixels: list[uint32]):
        """Return the number of dimensions of the data.

        Parameters
        ----------

        num_pixels: list[uint32]
            List of number of pixels per dimension.

        Returns
        -------

        n_dims: int
            Number of dimensions for which the number of pixels is larger than 1.
        """
        n_dims = int(np.sum(np.array(num_pixels) > 1))
        return n_dims

    @staticmethod
    def _get_numpy_data_type(
        data_type_on_disk: uint32,
    ) -> tuple[Union[np.dtype, None], Union[str, None]]:
        """Get the NumPy data type corresponding to the stored datatype.

        Parameters
        ----------

        data_type_on_disk: uint32
            UInt32 value from the stack metadata indicating the type of the data.

        Returns
        -------

        numpy_type: np.dtype
            Numpy dtype class. If the data type is not supported, returns None instead.

        str_type: str
            Type string (little endian). If the data type is not supported, returns None instead.
        """
        if data_type_on_disk == 0x00000001:
            return np.uint8, "<u1"
        elif data_type_on_disk == 0x00000002:
            return np.int8, "<i1"
        elif data_type_on_disk == 0x00000004:
            return np.uint16, "<u2"
        elif data_type_on_disk == 0x00000008:
            return np.int16, "<i2"
        elif data_type_on_disk == 0x00000010:
            return np.uint32, "<u4"
        elif data_type_on_disk == 0x00000020:
            return np.int32, "<i4"
        elif data_type_on_disk == 0x00000040:
            return np.float32, "<f4"
        elif data_type_on_disk == 0x00000080:
            return np.float64, "<f8"
        elif data_type_on_disk == 0x00001000:
            return np.uint64, "<u8"
        elif data_type_on_disk == 0x00002000:
            return np.int64, "<i8"
        else:
            return None, None

    def _read_obf_header(self, f: BinaryIO) -> bool:
        """Read the OBF header.

        Parameters
        ----------

        f: BinaryIO
            Open file handle.

        Returns
        -------
        success: bool
            True if reading the file header was successful, False otherwise.
        """

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
    ) -> tuple[bool, OBFStackMetadata]:
        """Read current OBF stack metadata (header + footer).

        Parameters
        ----------

        f: BinaryIO
            Open file handle.

        next_stack_pos: int
            Position in file where the next stack starts.

        Returns
        -------

        success: bool
            Whether parsing was successful.

        obf_stack_metadata: OBFStackMetadata
            OFBStackMetadata object.
        """

        # Initialize the metadata
        obf_stack_metadata = OBFStackMetadata()

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
        self, f: BinaryIO, obf_stack_metadata: OBFStackMetadata
    ) -> tuple[bool, OBFStackMetadata]:
        """Read the OBF stack header and update metadata.

        The file should already be positioned at the right location.

        Parameters
        ----------

        f: BinaryIO
            File handle to open.

        obf_stack_metadata: OBFStackMetadata
            Current OFBStackMetadata object

        Returns
        -------

        success: bool
            Whether parsing was successful.

        obf_stack_metadata: OBFStackMetadata
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
        for i in range(_Constants.BF_MAX_DIMENSIONS):
            n = struct.unpack("<I", f.read(4))[0]
            if i < obf_stack_metadata.rank:
                obf_stack_metadata.num_pixels.append(n)

        # Get the physical lengths along each dimension
        obf_stack_metadata.physical_lengths = []
        for i in range(_Constants.BF_MAX_DIMENSIONS):
            p = struct.unpack("<d", f.read(8))[0]
            if i < obf_stack_metadata.rank:
                obf_stack_metadata.physical_lengths.append(p)

        # Get the physical lengths along each dimension
        obf_stack_metadata.physical_offsets = []
        for i in range(_Constants.BF_MAX_DIMENSIONS):
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
        obf_stack_metadata.bytes_per_sample = self._get_bytes_per_sample_from_data_type(
            obf_stack_metadata.data_type_on_disk
        )

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

        # Now we are at the beginning of the stack (image or other)
        obf_stack_metadata.data_start_position = f.tell()

        # Start position of the footer
        footer_start_position = (
            obf_stack_metadata.data_start_position + obf_stack_metadata.data_len_disk
        )

        # Move to the beginning of the footer
        f.seek(footer_start_position)

        return True, obf_stack_metadata

    def _read_obf_stack_footer(self, f: BinaryIO, obf_stack_metadata: OBFStackMetadata):
        """Process footer.

        Parameters
        ----------
        f: BinaryIO
            Open file handle.

        obf_stack_metadata: OBFStackMetadata
            Metadata object for current stack.

        Returns
        -------

        obf_stack_metadata: OBFFileMetadata
            Updated metadata object for current stack.
        """

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
        size_for_version = self._get_footer_struct_size(
            obf_stack_metadata.format_version
        )

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
        for i in range(_Constants.BF_MAX_DIMENSIONS):
            p = struct.unpack("<I", f.read(4))[0]
            if i < obf_stack_metadata.rank:
                col_positions_present.append(p != 0)
            current_size += 4
        obf_stack_metadata.has_col_positions = col_positions_present

        # Entries are != 0 for all axes that have a label (after the footer)
        col_labels_present = []
        for i in range(_Constants.BF_MAX_DIMENSIONS):
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
            current_size == _Constants.V1A_FOOTER_LENGTH
        ), "Unexpected length of version 1/1A data."

        # Have we read enough for this version?
        if current_size > size_for_version:
            return obf_stack_metadata

        #
        # Version 2
        #

        # SI units of the value carried
        fractions = []
        for i in range(_Constants.OBF_SI_FRACTION_NUM_ELEMENTS):
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
        for i in range(_Constants.BF_MAX_DIMENSIONS):
            fractions = []
            for j in range(_Constants.OBF_SI_FRACTION_NUM_ELEMENTS):
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
            current_size == _Constants.V2_FOOTER_LENGTH
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
            current_size == _Constants.V3_FOOTER_LENGTH
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
            current_size == _Constants.V4_FOOTER_LENGTH
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
            current_size == _Constants.V5A_FOOTER_LENGTH
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
            current_size == _Constants.V6_FOOTER_LENGTH
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
                # Get value
                new_value = self._read_string(f, as_str=True, as_utf8=True)

                # Try to process it
                try:
                    tree = ET.fromstring(new_value)
                except ET.ParseError:
                    # Some keys are not XML, but stringified dictionaries
                    try:
                        tree = json.loads(new_value)
                    except json.JSONDecodeError as e:
                        print(
                            f"Failed processing value for key '{new_key}' ({e}): storing as raw string."
                        )
                        tree = new_value

                # Store it without further processing
                tag_dictionary[new_key] = tree

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

    def _scan_metadata(
        self, f: BinaryIO, obf_file_header: OBFFileHeader
    ) -> Union[OBFFileMetadata, None]:
        """Scan the metadata at the location stored in the header.

        The expected values are a key matching: "ome_xml" followed by
        valid OME XML metadata that we parse and return as an ElementTree.

        Parameters
        ----------

        f: BinaryIO
            Open file handle.

        obf_file_header: OBFFileHeader
            File header structure.

        Returns
        -------

        metadata: OBFFileMetadata
            OME-XML file metadata.
        """

        if obf_file_header.meta_data_position == 0:
            return None

        # Remember current position
        current_pos = f.tell()

        # Move to the beginning of the metadata
        f.seek(obf_file_header.meta_data_position)

        # Initialize OBFFileMetadata object
        metadata = OBFFileMetadata()

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
    def _read_string(
        f: BinaryIO, as_str: bool = True, as_utf8: bool = True
    ) -> Union[str, bytes]:
        """Read a string at current position.

        Parameters
        ----------

        f: BinaryIO
            Open file handles.

        as_str: bool = True
            If True parse the raw byte array to string.

        as_utf8: bool = True
            If True decode the string to utf-8. Ignored if as_str is False.

        Returns
        -------

        string: Union[bytes, str]
            Either raw bytes or a str, optionally utf-8 encoded.
        """

        # Read the length of the following string
        length = struct.unpack("<I", f.read(4))[0]
        if length == 0:
            return ""

        # Read `length` bytes and convert them to utf-8 if requested
        value = f.read(length)
        if as_str:
            if as_utf8:
                value = value.decode("utf-8")

        return value

    @staticmethod
    def _get_bytes_per_sample_from_data_type(data_type: uint32) -> int:
        """Return the number of bytes per sample for given data type."""
        supported_types = {
            0x00000001: 1,  # 8-bit unsigned byte
            0x00000002: 1,  # 8-bit signed char
            0x00000004: 2,  # 16-bit word value
            0x00000008: 2,  # 16-bit signed integer
            0x00000010: 4,  # 32-bit unsigned integer
            0x00000020: 4,  # 32-bit signed integer
            0x00000040: 4,  # 32-bit floating point value
            0x00000080: 8,  # 64-bit floating point value
        }

        # Get the number of bytes
        num_bytes_per_sample = supported_types.get(data_type, -1)

        # Check that it is supported
        if num_bytes_per_sample == -1:
            raise ValueError(f"Unsupported data type 0x{data_type:08x}.")

        # Return it
        return num_bytes_per_sample

    def get_image_info_list(self):
        """Return a list of images from all stacks."""

        # Initialize the list
        images = []

        # Do we have images?
        if self.num_stacks == 0:
            return images

        for i, stack in enumerate(self._obf_stacks_list):

            # Only return images
            if (np.array(stack.num_pixels) > 1).sum() == 2:

                # Get pixel size
                pixel_sizes = np.round(
                    np.array(self.get_data_pixel_sizes(stack_index=i)) * 1e9, 2
                )[:2]

                # Get detector
                detector = self._get_detector(
                    imspector_dictionary_root=stack.tag_dictionary["imspector"],
                    img_name=stack.stack_name,
                )

                if detector is None:
                    continue

                # Build a (univocal) summary string
                as_string = (
                    f"{detector}: {stack.stack_name}: "
                    f"size = (h={stack.num_pixels[1]} x w={stack.num_pixels[0]}); "
                    f"pixel size = {pixel_sizes[0]}nm "
                    f"(index = {i})"
                )
                images.append(
                    {
                        "index": i,
                        "name": stack.stack_name,
                        "detector": detector,
                        "description": stack.stack_description,
                        "num_pixels": stack.num_pixels,
                        "physical_lengths": stack.physical_lengths,
                        "physical_offsets": stack.physical_offsets,
                        "pixel_sizes": pixel_sizes,
                        "as_string": as_string,
                    }
                )

        # Sort the list using natural sorting by the 'as_string' key
        images = natsorted(images, key=lambda x: x["as_string"])

        # Return the extracted metadata
        return images

    def get_image_info_dict(self):
        """Return a hierarchical dictionary of images from all stacks."""

        # Initialize the dictionary
        images = {}

        # Do we have images?
        if self.num_stacks == 0:
            return images

        for i, stack in enumerate(self._obf_stacks_list):

            # Only return images
            if (np.array(stack.num_pixels) > 1).sum() == 2:

                # Get pixel size
                pixel_sizes = np.round(
                    np.array(self.get_data_pixel_sizes(stack_index=i)) * 1e9, 2
                )[:2]

                # Get detector
                detector = self._get_detector(
                    imspector_dictionary_root=stack.tag_dictionary["imspector"],
                    img_name=stack.stack_name,
                )

                if detector is None:
                    continue

                # Get acquisition number
                match = re.match(
                    r"^.+{(?P<index>\d+)}(?P<extra>.*)$",
                    stack.stack_name,
                    re.IGNORECASE,
                )
                if match:
                    if match["extra"] == "":
                        key = f"Image {match['index']}"
                    else:
                        key = f"Image {match['index']} ({match['extra']})"
                else:
                    key = stack.stack_name

                if key in images:
                    image = images[key]
                else:
                    image = {
                        "metadata": "",
                        "detectors": [],
                    }

                # Metadata
                frame_size = (
                    stack.num_pixels[0] * pixel_sizes[0] / 1000,
                    stack.num_pixels[1] * pixel_sizes[1] / 1000,
                )

                # Build metadata string
                metadata = f"Frame: {frame_size[0]:.1f}x{frame_size[1]:.1f}µm - Pixel: {pixel_sizes[0]}nm"
                if image["metadata"] == "":
                    image["metadata"] = metadata
                else:
                    if image["metadata"] != metadata:
                        raise ValueError(
                            f"The same detector seems to have inconsistent metadata across acquisitions!"
                        )

                # Append current detectir
                image["detectors"].append(
                    {
                        "index": i,
                        "name": stack.stack_name,
                        "detector": detector,
                        "description": stack.stack_description,
                        "num_pixels": stack.num_pixels,
                        "physical_lengths": stack.physical_lengths,
                        "physical_offsets": stack.physical_offsets,
                        "pixel_sizes": pixel_sizes,
                    }
                )

                # Store the (updated) image in the dictionary
                images[key] = image

        # Sort the dictionary using natural sorting of its keys
        images = dict(natsorted(images.items()))

        # Return the extracted metadata
        return images

    @staticmethod
    def _get_detector(imspector_dictionary_root: ET, img_name: str) -> Union[str, None]:
        """Extract the detector names from the tag dictionary of current stack.

        Parameters
        ----------

        imspector_dictionary_root: xml.etree.ElementTree
            Root of the "imspector" tree (i.e., tag_dictionary["imspector"]).

        Returns
        -------

        name: Union[str, None]
            Name of the detector, or None if the detector could not be found.
        """

        # Get the channels node
        channels_node = imspector_dictionary_root.find(
            "./doc/ExpControl/measurement/channels"
        )
        if channels_node is None:
            return None

        # Find all items
        items = channels_node.findall("item")
        if items is None:
            return None

        # Process items
        detector = None
        for item in items:
            detector = item.find("./detsel/detector")
            name = item.find("./name")
            if detector is not None and name is not None:
                if name.text in img_name:
                    return detector.text

        return detector
