"""Writes a decoded pixel matrix out to a .png file."""
import png

from extract_nes_graphics.constants import PALETTE


def save_png(path, pixel_matrix, palette=PALETTE):
    """Write a pixel matrix (as produced by decoder.decode_chr) to `path`."""
    with open(path, 'wb') as png_file:
        writer = png.Writer(len(pixel_matrix[0]), len(pixel_matrix), palette=palette)
        writer.write(png_file, pixel_matrix)
