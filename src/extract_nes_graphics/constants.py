"""Shared constants for CHR decoding."""

# RGB palette used to render the 2-bit NES/Famicom tile pixels as a PNG.
# Index 0-3 map directly to the 2-bit color values produced by decode_chr().
PALETTE = [(0, 0, 0), (255, 0, 0), (0, 0, 255), (255, 255, 255)]

# Number of 8x8 tiles placed on each row of the resulting image: 16 is the
# conventional width for viewing NES/Famicom CHR data (one 4KB pattern
# table is organized as a 16x16 tile grid), giving a fixed 128px-wide
# output regardless of how many tiles the source file has.
TILES_IN_ROW = 16
