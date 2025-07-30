import gzip
import struct
from typing import List, Dict


class PSFParseError(Exception):
    pass


class PSFFont:
    def __init__(self, data: bytes):
        self.glyphs: List[List[List[bool]]] = []  # Store as 2D pixel arrays
        self.unicode_map: Dict[int, List[int]] = {}
        self.width: int = 8
        self.height: int = 0
        self._parse(data)

    def _parse(self, data: bytes):
        if data[0:2] == b"\x36\x04":
            self._parse_psf1(data)
        elif data[0:4] == b"\x72\xb5\x4a\x86":
            self._parse_psf2(data)
        else:
            raise PSFParseError("Not a PSF file")

    def _parse_psf1(self, data: bytes):
        mode = data[2]
        height = data[3]

        if mode > 0x111:
            raise PSFParseError("Unknown mode")

        glyphs = 512 if mode & 0b001 else 256
        width = 8
        char_size = height
        bytes_per_row = 1

        self.height = height
        self.width = width
        self.flags = 0
        self.headersize = 4
        self.length = glyphs
        self.charsize = char_size
        self.glyph_data_start = 4
        self.glyph_data_length = glyphs * char_size
        self.unicode_data_start = 4 + glyphs * char_size
        self.unicode_data_length = len(data) - self.unicode_data_start

        # Read glyphs using Perl logic
        self._read_glyphs(data, 4, glyphs, height, width, char_size, bytes_per_row)

    def _parse_psf2(self, data: bytes):
        header = struct.unpack("<7I", data[4:32])  # Skip magic, read 7 values
        (
            version,
            header_size,
            flags,
            glyphs,
            char_size,
            height,
            width,
        ) = header

        if version != 0:
            raise PSFParseError("Unknown sub-version")
        if header_size != 32:
            raise PSFParseError("Unknown header size")

        bytes_per_row = (width + 7) // 8
        if char_size != height * bytes_per_row:
            raise PSFParseError("Mismatch in char byte size")

        self.height = height
        self.width = width
        self.flags = flags
        self.headersize = header_size
        self.length = glyphs
        self.charsize = char_size
        self.glyph_data_start = header_size
        self.glyph_data_length = glyphs * char_size
        self.unicode_data_start = header_size + glyphs * char_size
        self.unicode_data_length = len(data) - self.unicode_data_start

        # Read glyphs using Perl logic
        self._read_glyphs(data, header_size, glyphs, height, width, char_size, bytes_per_row)

        # Parse unicode table if present
        if flags & 1:
            self._parse_unicode_table(data, header_size + glyphs * char_size)

    def _read_glyphs(
        self, data: bytes, offset: int, glyph_count: int, height: int, width: int, char_size: int, bytes_per_row: int
    ):
        """Read glyphs exactly like the Perl script"""
        data_pos = offset

        for glyph_idx in range(glyph_count):
            glyph_pixels = []

            for y in range(height):
                row_pixels = []
                x = 0

                for byte_idx in range(bytes_per_row):
                    if data_pos < len(data):
                        byte_value = data[data_pos]
                        data_pos += 1
                    else:
                        byte_value = 0

                    # Process bits MSB first (bit 8 down to 1)
                    for bit in range(8):
                        if x < width:  # Only if within width
                            pixel_on = bool(byte_value & (1 << (7 - bit)))
                            row_pixels.append(pixel_on)
                            x += 1

                glyph_pixels.append(row_pixels)

            self.glyphs.append(glyph_pixels)

    def _parse_unicode_table(self, data: bytes, offset: int):
        """Parse PSF2 unicode mapping table"""
        pos = offset
        glyph_index = 0

        while pos < len(data) and glyph_index < len(self.glyphs):
            unicode_list = []

            # Read unicode codepoints for this glyph
            while pos < len(data):
                if pos + 1 < len(data):
                    # Read 16-bit unicode value
                    unicode_val = struct.unpack("<H", data[pos : pos + 2])[0]
                    pos += 2

                    if unicode_val == 0xFFFF:
                        # End of sequence for this glyph
                        break
                    elif unicode_val == 0xFFFE:
                        # Start of sequence - not implemented
                        continue
                    else:
                        unicode_list.append(unicode_val)
                else:
                    break

            if unicode_list:
                self.unicode_map[glyph_index] = unicode_list

            glyph_index += 1


def load_psf_file(path):
    with gzip.open(path, "rb") if str(path).endswith(".gz") else open(path, "rb") as f:
        data = f.read()
    return PSFFont(data)
