"""extract_nes_graphics: converts NES/Famicom CHR tile data into PNG images.

The GUI (and its tkinter dependency) is intentionally not imported here, so
the pure decoding/batch modules can be used and tested without tkinter
installed. Use `extract_nes_graphics.gui.main()` or run the package
(`python -m extract_nes_graphics`) to launch the GUI.
"""


def main():
    from extract_nes_graphics.gui import main as gui_main
    gui_main()
