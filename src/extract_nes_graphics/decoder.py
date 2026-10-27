"""Pure CHR -> pixel matrix decoding logic.

No file or GUI side effects live here on purpose: this module only turns raw
CHR bytes into the nested pixel matrix that png_writer.save_png() can write
out, which keeps it simple to unit test.
"""
import numpy

from extract_nes_graphics.constants import TILES_IN_ROW

TILE_SIZE_BYTES = 16  # 2 bitplanes of 8 bytes each


def chr_bytes_to_tile_pixels(data):
    """Decode raw CHR bytes into an (N, 8, 8) array of 2-bit palette indices.

    Each 16-byte tile is two 8x8 bitplanes; a pixel's value is
    plane0_bit + 2*plane1_bit. This decodes every tile in `data` in a
    handful of vectorized numpy operations instead of looping over tiles
    in Python and converting each one through hex strings and bin().
    """
    if len(data) % TILE_SIZE_BYTES != 0:
        raise ValueError(
            'CHR data length (%d bytes) is not a multiple of %d (one tile).'
            % (len(data), TILE_SIZE_BYTES)
        )

    tile_count = len(data) // TILE_SIZE_BYTES
    if tile_count == 0:
        return numpy.empty((0, 8, 8), dtype=numpy.uint8)

    tiles = numpy.frombuffer(data, dtype=numpy.uint8).reshape(tile_count, TILE_SIZE_BYTES)
    plane0_bits = numpy.unpackbits(tiles[:, :8], axis=1).reshape(tile_count, 8, 8)
    plane1_bits = numpy.unpackbits(tiles[:, 8:], axis=1).reshape(tile_count, 8, 8)
    return plane0_bits + 2 * plane1_bits


def decode_chr(data, tiles_in_row=TILES_IN_ROW):
    """Decode raw CHR bytes into the full pixel matrix for the output PNG.

    Tiles are laid out left-to-right, top-to-bottom, `tiles_in_row` tiles
    wide (16 by default - see TILES_IN_ROW). The image is exactly that
    wide regardless of how many tiles `data` contains; only its height
    varies with the file size. A source with fewer tiles than
    `tiles_in_row` simply produces a narrower first (and only) row.
    """
    tile_pixels = chr_bytes_to_tile_pixels(data)
    size_chr = len(tile_pixels)
    img_htiles = max(1, tiles_in_row)

    mega_pixel = list(tile_pixels)

    reshape = [mega_pixel[index:index + img_htiles] for index in range(0, size_chr, img_htiles)]
    reshape.append([numpy.zeros((8, 8), dtype=numpy.uint8)])

    if len(reshape[-1]) < len(reshape[-2]):
        fill = len(reshape[-2]) - len(reshape[-1])
        for _ in range(fill):
            reshape[-1].append(numpy.zeros((8, 8), dtype=numpy.uint8))

    return [
        entry
        for row in range(len(reshape))
        for entry in numpy.hstack(reshape[row])
    ]
