"""Orchestrates converting a single CHR/NES file or a whole folder of them.

This is the non-GUI equivalent of the original convertFile()/converter()
methods: it reads the input file(s), decodes them and writes the resulting
PNG(s), without any Tkinter dependency so it can be driven from tests or a
future CLI.
"""
import os
import time

from extract_nes_graphics.conversion_log import write_log
from extract_nes_graphics.decoder import decode_chr
from extract_nes_graphics.ines import extract_chr
from extract_nes_graphics.png_writer import save_png

CONVERTIBLE_EXTENSIONS = ('.chr', '.nes')


def is_convertible(filename):
    return filename.lower().endswith(CONVERTIBLE_EXTENSIONS)


def read_chr_data(filename):
    """Read the raw CHR bytes to decode from a .chr or .nes file.

    A .chr file is treated as raw CHR data. A .nes file is a full iNES ROM,
    so its CHR ROM bank is located and extracted via the header instead of
    decoding the whole file (which would mix in the header and PRG code).
    """
    with open(filename, 'rb') as source_file:
        data = source_file.read()
    if filename.lower().endswith('.nes'):
        return extract_chr(data)
    return data


def convert_single_file(filename, save_dir):
    """Decode `filename` and write the resulting PNG into `save_dir`."""
    data = read_chr_data(filename)
    pixel_matrix = decode_chr(data)
    output_path = os.path.join(save_dir, os.path.split(filename)[1] + '.png')
    save_png(output_path, pixel_matrix)
    return output_path


def convert_folder(dump_dir, save_dir=None):
    """Convert every .chr/.nes file directly inside `dump_dir`.

    Writes LOG.TXT into `dump_dir` summarizing the run. Returns
    (good_files, bad_files) counts.
    """
    save_dir = save_dir or dump_dir
    good_files = 0
    bad_files = 0
    list_bad_files = ''
    starting_at = time.strftime('%x - %X')

    for a_file in sorted(x for x in os.listdir(dump_dir) if is_convertible(x)):
        full_path = dump_dir + '/' + a_file
        try:
            convert_single_file(full_path, save_dir)
            good_files += 1
        except:
            bad_files += 1
            list_bad_files += '@@' + a_file
        write_log(dump_dir, good_files, bad_files, list_bad_files, starting_at, time.strftime('%x - %X'))

    return good_files, bad_files
