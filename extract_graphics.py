"""Backwards-compatible entry point: `python extract_graphics.py`.

The actual implementation now lives in the extract_nes_graphics package
under src/. This thin wrapper is kept so the usage documented in the
README keeps working.
"""
from extract_nes_graphics.gui import main

if __name__ == '__main__':
    main()
