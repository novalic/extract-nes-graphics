"""Tests for extract_nes_graphics.batch (non-GUI conversion orchestration)."""
import os

import pytest

from extract_nes_graphics.batch import convert_folder, convert_single_file, is_convertible

# A minimal CHR payload that doesn't trip the current "fewer tiles than
# tiles_in_row" bug (see test_decoder.py): exactly 128 solid-black tiles.
VALID_CHR_BYTES = bytes(128 * 16)


class TestIsConvertible:
    @pytest.mark.parametrize('name', ['sprites.chr', 'SPRITES.CHR', 'game.nes', 'game.NES'])
    def test_recognizes_chr_and_nes_regardless_of_case(self, name):
        assert is_convertible(name) is True

    @pytest.mark.parametrize('name', ['readme.txt', 'LOG.TXT', 'sprites.chrx', ''])
    def test_rejects_anything_else(self, name):
        assert is_convertible(name) is False


class TestConvertSingleFile:
    def test_writes_a_png_next_to_the_source_by_default_name(self, tmp_path):
        chr_file = tmp_path / 'sprites.chr'
        chr_file.write_bytes(VALID_CHR_BYTES)

        output_path = convert_single_file(str(chr_file), str(tmp_path))

        assert output_path == str(tmp_path / 'sprites.chr.png')
        assert os.path.exists(output_path)

    def test_can_write_into_a_different_save_dir(self, tmp_path):
        src_dir = tmp_path / 'src'
        dst_dir = tmp_path / 'dst'
        src_dir.mkdir()
        dst_dir.mkdir()
        chr_file = src_dir / 'sprites.chr'
        chr_file.write_bytes(VALID_CHR_BYTES)

        output_path = convert_single_file(str(chr_file), str(dst_dir))

        assert output_path == str(dst_dir / 'sprites.chr.png')
        assert os.path.exists(output_path)

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            convert_single_file(str(tmp_path / 'missing.chr'), str(tmp_path))

    def test_fewer_than_128_tiles_still_converts(self, tmp_path):
        # Any whole number of tiles converts fine, however small.
        chr_file = tmp_path / 'tiny.chr'
        chr_file.write_bytes(bytes(16))  # 1 tile
        output_path = convert_single_file(str(chr_file), str(tmp_path))
        assert os.path.exists(output_path)

    def test_truncated_tile_raises(self, tmp_path):
        # A file whose length isn't a multiple of 16 bytes has a partial
        # trailing tile, which fails to decode.
        chr_file = tmp_path / 'truncated.chr'
        chr_file.write_bytes(bytes(20))
        with pytest.raises(ValueError):
            convert_single_file(str(chr_file), str(tmp_path))


class TestConvertFolder:
    def test_converts_only_chr_and_nes_files_in_the_folder(self, tmp_path):
        (tmp_path / 'a.chr').write_bytes(VALID_CHR_BYTES)
        (tmp_path / 'b.nes').write_bytes(VALID_CHR_BYTES)
        (tmp_path / 'notes.txt').write_text('ignore me')

        good, bad = convert_folder(str(tmp_path))

        assert good == 2
        assert bad == 0
        assert (tmp_path / 'a.chr.png').exists()
        assert (tmp_path / 'b.nes.png').exists()
        assert not (tmp_path / 'notes.txt.png').exists()

    def test_counts_failures_without_stopping_the_batch(self, tmp_path):
        (tmp_path / 'good.chr').write_bytes(VALID_CHR_BYTES)
        (tmp_path / 'bad.chr').write_bytes(bytes(20))  # truncated tile, will fail

        good, bad = convert_folder(str(tmp_path))

        assert good == 1
        assert bad == 1
        assert (tmp_path / 'good.chr.png').exists()

    def test_writes_log_txt_with_the_failed_file_name(self, tmp_path):
        (tmp_path / 'bad.chr').write_bytes(bytes(20))  # truncated tile, will fail

        convert_folder(str(tmp_path))

        log_text = (tmp_path / 'LOG.TXT').read_text()
        assert 'bad.chr' in log_text
        assert 'Not converted (ERROR): 1' in log_text

    def test_can_write_output_into_a_separate_save_dir(self, tmp_path):
        src_dir = tmp_path / 'src'
        dst_dir = tmp_path / 'dst'
        src_dir.mkdir()
        dst_dir.mkdir()
        (src_dir / 'a.chr').write_bytes(VALID_CHR_BYTES)

        good, bad = convert_folder(str(src_dir), str(dst_dir))

        assert good == 1
        assert bad == 0
        assert (dst_dir / 'a.chr.png').exists()
        assert (src_dir / 'LOG.TXT').exists()
