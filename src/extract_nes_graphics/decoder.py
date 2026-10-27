"""Pure CHR -> pixel matrix decoding logic.

No file or GUI side effects live here on purpose: this module only turns raw
CHR bytes into the nested pixel matrix that png_writer.save_png() can write
out, which keeps it simple to unit test.
"""
import binascii

import numpy

from extract_nes_graphics.constants import TILES_IN_ROW


def chr_bytes_to_tiles(data):
    """Split raw CHR bytes into a list of 32-hex-char tile strings.

    Each NES/Famicom tile is 16 bytes (2 bitplanes of 8 bytes each), which is
    32 hex characters once hex-encoded.
    """
    in_hex = binascii.hexlify(data).decode('ascii')
    return [in_hex[index:index + 32] for index in range(0, len(in_hex), 32)]


def tile_hex_to_pixels(tile_hex):
    """Decode one 32-hex-char CHR tile into an 8x8 matrix of palette indices.

    Each NES tile is stored as two 8x8 bitplanes; the pixel's 2-bit palette
    index is plane0_bit + 2*plane1_bit.
    """
    plane0 = [int(bit) for bit in bin(int(tile_hex[:16], 16))[2:].zfill(64)]
    plane1 = [int(bit) for bit in bin(int(tile_hex[16:], 16))[2:].zfill(64)]
    decoded = [x + 2 * y for x, y in zip(plane0, plane1)]
    return [decoded[index:index + 8] for index in range(0, len(decoded), 8)]


def decode_chr(data, tiles_in_row=TILES_IN_ROW):
    """Decode raw CHR bytes into the full pixel matrix for the output PNG."""
    tiles = chr_bytes_to_tiles(data)
    size_chr = len(tiles)
    # At least 1 tile per row, even when there are fewer tiles than
    # tiles_in_row (previously this truncated to 0, and range() rejects a
    # zero step).
    img_htiles = max(1, int(size_chr / tiles_in_row))

    mega_pixel = [tile_hex_to_pixels(tile) for tile in tiles]

    reshape = [mega_pixel[index:index + img_htiles] for index in range(0, size_chr, img_htiles)]
    reshape.append([[[0, 0, 0, 0, 0, 0, 0, 0]] * 8])

    if len(reshape[-1]) < len(reshape[-2]):
        fill = len(reshape[-2]) - len(reshape[-1])
        for _ in range(fill):
            reshape[-1].append([[0, 0, 0, 0, 0, 0, 0, 0]] * 8)

    return [
        entry
        for row in range(len(reshape))
        for entry in numpy.hstack(reshape[row])
    ]
