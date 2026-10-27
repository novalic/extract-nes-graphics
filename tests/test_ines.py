"""Tests for extract_nes_graphics.ines (iNES header parsing)."""
import pytest

from extract_nes_graphics.ines import extract_chr


def build_ines(chr_data, prg_size=16384, has_trainer=False):
    """Build a minimal synthetic iNES file wrapping the given CHR bytes."""
    prg_units = prg_size // 16384
    chr_units = len(chr_data) // 8192
    flags6 = 0b00000100 if has_trainer else 0
    header = bytes([0x4E, 0x45, 0x53, 0x1A, prg_units, chr_units, flags6, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    trainer = bytes(512) if has_trainer else b''
    prg_data = bytes(prg_size)
    return header + trainer + prg_data + chr_data


class TestExtractChr:
    def test_returns_the_chr_bank_bytes(self):
        chr_data = bytes(range(256)) * 32  # 8192 bytes, 1 CHR unit
        nes_file = build_ines(chr_data)

        assert extract_chr(nes_file) == chr_data

    def test_skips_the_trainer_when_present(self):
        chr_data = bytes([0xAB]) * 8192
        nes_file = build_ines(chr_data, has_trainer=True)

        assert extract_chr(nes_file) == chr_data

    def test_locates_chr_after_a_larger_prg_bank(self):
        chr_data = bytes([0xCD]) * 8192
        nes_file = build_ines(chr_data, prg_size=16384 * 2)

        assert extract_chr(nes_file) == chr_data

    def test_raises_for_missing_ines_magic(self):
        with pytest.raises(ValueError):
            extract_chr(b'not a nes file' + bytes(100))

    def test_raises_when_there_is_no_chr_rom(self):
        header = bytes([0x4E, 0x45, 0x53, 0x1A, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        nes_file = header + bytes(16384)

        with pytest.raises(ValueError):
            extract_chr(nes_file)
