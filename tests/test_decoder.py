"""Tests for extract_nes_graphics.decoder (pure CHR -> pixel-matrix logic)."""
import binascii

import pytest

from extract_nes_graphics.decoder import (
    chr_bytes_to_tiles,
    decode_chr,
    tile_hex_to_pixels,
)


def _solid_tile_bytes(value):
    """16 raw bytes for a tile whose every pixel decodes to `value` (0-3)."""
    plane0_byte = 0xFF if value & 0b01 else 0x00
    plane1_byte = 0xFF if value & 0b10 else 0x00
    return bytes([plane0_byte] * 8) + bytes([plane1_byte] * 8)


class TestChrBytesToTiles:
    def test_splits_data_into_32_char_hex_chunks(self):
        data = bytes(range(16)) * 2  # 32 bytes -> 2 tiles
        tiles = chr_bytes_to_tiles(data)
        assert tiles == [
            binascii.hexlify(data[:16]).decode('ascii'),
            binascii.hexlify(data[16:]).decode('ascii'),
        ]

    def test_empty_input_gives_no_tiles(self):
        assert chr_bytes_to_tiles(b'') == []

    def test_partial_trailing_tile_is_kept_as_a_short_chunk(self):
        data = bytes(20)  # one full 16-byte tile + 4 leftover bytes
        tiles = chr_bytes_to_tiles(data)
        assert len(tiles) == 2
        assert len(tiles[0]) == 32
        assert len(tiles[1]) == 8  # 4 bytes -> 8 hex chars


class TestTileHexToPixels:
    def test_all_zero_tile_decodes_to_all_zero_pixels(self):
        tile_hex = _solid_tile_bytes(0).hex()
        pixels = tile_hex_to_pixels(tile_hex)
        assert pixels == [[0] * 8 for _ in range(8)]

    @pytest.mark.parametrize('value', [0, 1, 2, 3])
    def test_solid_tile_decodes_to_uniform_value(self, value):
        tile_hex = _solid_tile_bytes(value).hex()
        pixels = tile_hex_to_pixels(tile_hex)
        assert pixels == [[value] * 8 for _ in range(8)]

    def test_mixed_planes_combine_as_plane0_plus_2_times_plane1(self):
        # First byte of plane0 = 0b10000000 -> first pixel of first row has
        # plane0 bit 1; first byte of plane1 = 0 -> plane1 bit 0.
        plane0 = bytes([0b10000000] + [0] * 7)
        plane1 = bytes([0] * 8)
        tile_hex = (plane0 + plane1).hex()
        pixels = tile_hex_to_pixels(tile_hex)
        assert pixels[0][0] == 1
        assert pixels[0][1] == 0

    def test_returns_8_rows_of_8_columns(self):
        pixels = tile_hex_to_pixels(_solid_tile_bytes(3).hex())
        assert len(pixels) == 8
        assert all(len(row) == 8 for row in pixels)


class TestDecodeChr:
    def test_decodes_a_grid_of_solid_tiles_with_padding_row(self):
        # 4 tiles, 2 per row -> reshape ends up as 3 rows of 2 tiles once the
        # padding (black) row is appended, since the last row only had 0
        # tiles of content before padding. Image is 16px wide, 24px tall.
        tiles_data = b''.join(_solid_tile_bytes(v) for v in (0, 1, 2, 3))
        result = decode_chr(tiles_data, tiles_in_row=2)

        assert len(result) == 24
        assert all(len(row) == 16 for row in result)

        # Row 0 is tile0 (value 0) hstacked with tile1 (value 1).
        assert list(result[0][:8]) == [0] * 8
        assert list(result[0][8:]) == [1] * 8
        # Row 8 is tile2 (value 2) hstacked with tile3 (value 3).
        assert list(result[8][:8]) == [2] * 8
        assert list(result[8][8:]) == [3] * 8
        # The appended padding row is pure black (0).
        assert list(result[16][:8]) == [0] * 8
        assert list(result[16][8:]) == [0] * 8

    def test_fewer_tiles_than_tiles_in_row_uses_a_single_tile_per_row(self):
        # Previously img_htiles truncated to 0 here and range() rejected
        # the zero step; it now floors to 1 tile per row instead.
        tiles_data = _solid_tile_bytes(1) + _solid_tile_bytes(2)
        result = decode_chr(tiles_data, tiles_in_row=128)

        assert len(result) == 24  # 2 content rows + 1 padding row, 8px each
        assert all(len(row) == 8 for row in result)
        assert list(result[0]) == [1] * 8
        assert list(result[8]) == [2] * 8
        assert list(result[16]) == [0] * 8

    def test_partial_trailing_tile_raises_value_error(self):
        # A CHR file whose length isn't a multiple of 16 bytes produces a
        # short last tile; its second bitplane hex-decodes to an empty
        # string, which int(..., 16) rejects.
        tiles_data = _solid_tile_bytes(0) + bytes(4)
        with pytest.raises(ValueError):
            decode_chr(tiles_data, tiles_in_row=128)
