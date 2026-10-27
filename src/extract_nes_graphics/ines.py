"""Parses the iNES (.nes) header to locate the embedded CHR ROM bank.

Without this, treating a whole .nes file as raw CHR data (as the original
script did) decodes the 16-byte header and the PRG ROM program code as if
they were tile graphics, producing garbage pixels mixed in with the real
tiles.
"""

INES_MAGIC = b'NES\x1a'
HEADER_SIZE = 16
TRAINER_SIZE = 512
PRG_UNIT_SIZE = 16384  # 16 KiB per PRG ROM unit (header byte 4)
CHR_UNIT_SIZE = 8192  # 8 KiB per CHR ROM unit (header byte 5)


def extract_chr(data):
    """Return the raw CHR ROM bytes embedded in an iNES (.nes) file.

    Raises ValueError if `data` isn't a valid iNES file, or if it has no
    CHR ROM at all (CHR-RAM carts store no tile data in the file).
    """
    if data[:4] != INES_MAGIC:
        raise ValueError('Not a valid iNES (.nes) file: missing "NES\\x1a" header.')

    prg_units = data[4]
    chr_units = data[5]
    if chr_units == 0:
        raise ValueError('This .nes file has no CHR ROM (it uses CHR RAM).')

    has_trainer = bool(data[6] & 0b00000100)
    offset = HEADER_SIZE + (TRAINER_SIZE if has_trainer else 0) + prg_units * PRG_UNIT_SIZE
    chr_size = chr_units * CHR_UNIT_SIZE
    return data[offset:offset + chr_size]
