"""Shared constants for CHR decoding."""

# RGB palette used to render the 2-bit NES/Famicom tile pixels as a PNG.
# Index 0-3 map directly to the 2-bit color values produced by decode_chr().
PALETTE = [(0, 0, 0), (255, 0, 0), (0, 0, 255), (255, 255, 255)]

# Number of 8x8 tiles placed on each row of the resulting image.
TILES_IN_ROW = 128
