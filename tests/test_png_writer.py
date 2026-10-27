"""Tests for extract_nes_graphics.png_writer."""
import png

from extract_nes_graphics.constants import PALETTE
from extract_nes_graphics.png_writer import save_png


class TestSavePng:
    def test_writes_a_png_with_the_given_dimensions(self, tmp_path):
        pixel_matrix = [[0, 1, 2, 3], [3, 2, 1, 0]]
        out_file = tmp_path / 'out.png'

        save_png(str(out_file), pixel_matrix)

        assert out_file.exists()
        width, height, rows, meta = png.Reader(filename=str(out_file)).read()
        assert width == 4
        assert height == 2
        assert [list(row) for row in rows] == pixel_matrix

    def test_writes_the_given_palette(self, tmp_path):
        pixel_matrix = [[0, 1, 2, 3]]
        out_file = tmp_path / 'out.png'

        save_png(str(out_file), pixel_matrix, palette=PALETTE)

        _, _, _, meta = png.Reader(filename=str(out_file)).read()
        assert meta['palette'] == PALETTE

    def test_accepts_a_custom_palette(self, tmp_path):
        pixel_matrix = [[0, 1]]
        custom_palette = [(10, 20, 30), (40, 50, 60)]
        out_file = tmp_path / 'out.png'

        save_png(str(out_file), pixel_matrix, palette=custom_palette)

        _, _, _, meta = png.Reader(filename=str(out_file)).read()
        assert meta['palette'] == custom_palette
