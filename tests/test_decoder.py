"""Tests for extract_nes_graphics.decoder (pure CHR -> pixel-matrix logic)."""
import pytest

from extract_nes_graphics.decoder import chr_bytes_to_tile_pixels, decode_chr


def _solid_tile_bytes(value):
    """16 raw bytes for a tile whose every pixel decodes to `value` (0-3)."""
    plane0_byte = 0xFF if value & 0b01 else 0x00
    plane1_byte = 0xFF if value & 0b10 else 0x00
    return bytes([plane0_byte] * 8) + bytes([plane1_byte] * 8)


class TestChrBytesToTilePixels:
    def test_empty_input_gives_no_tiles(self):
        result = chr_bytes_to_tile_pixels(b'')
        assert len(result) == 0

    def test_all_zero_tile_decodes_to_all_zero_pixels(self):
        result = chr_bytes_to_tile_pixels(_solid_tile_bytes(0))
        assert result.tolist() == [[[0] * 8] * 8]

    @pytest.mark.parametrize('value', [0, 1, 2, 3])
    def test_solid_tile_decodes_to_uniform_value(self, value):
        result = chr_bytes_to_tile_pixels(_solid_tile_bytes(value))
        assert result.tolist() == [[[value] * 8] * 8]

    def test_decodes_multiple_tiles_in_order(self):
        data = _solid_tile_bytes(1) + _solid_tile_bytes(2)
        result = chr_bytes_to_tile_pixels(data)
        assert len(result) == 2
        assert result[0].tolist() == [[1] * 8] * 8
        assert result[1].tolist() == [[2] * 8] * 8

    def test_mixed_planes_combine_as_plane0_plus_2_times_plane1(self):
        # First byte of plane0 = 0b10000000 -> first pixel of first row has
        # plane0 bit 1; first byte of plane1 = 0 -> plane1 bit 0.
        plane0 = bytes([0b10000000] + [0] * 7)
        plane1 = bytes([0] * 8)
        result = chr_bytes_to_tile_pixels(plane0 + plane1)
        assert result[0][0][0] == 1
        assert result[0][0][1] == 0

    def test_partial_trailing_tile_raises_value_error(self):
        # A CHR file whose length isn't a multiple of 16 bytes has a
        # partial trailing tile, which can't be decoded.
        data = _solid_tile_bytes(0) + bytes(4)
        with pytest.raises(ValueError):
            chr_bytes_to_tile_pixels(data)


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
        tiles_data = _solid_tile_bytes(0) + bytes(4)
        with pytest.raises(ValueError):
            decode_chr(tiles_data, tiles_in_row=128)
