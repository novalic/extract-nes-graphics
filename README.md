# CHR to PNG

This is a basic tool to convert .nes or .chr files to a .png image. There might be some similar tools around the web, but I've been looking for one for quite some time and couldn't find one that worked neither on Linux or 64bit Windows. It was a really nice thing to do and it's part of some research I have been doing lately about he NES architecture. Also I included a nice and simple GUI.

## Some documentation

### Usage

Dependencies are managed with [uv](https://docs.astral.sh/uv/). A `Makefile` wraps the common commands:

```bash
make install    # create the venv and install dependencies
make run        # launch the GUI (python extract_graphics.py)
make test       # run the test suite
make coverage   # run the test suite with a coverage report
make check      # lint with ruff
make fix        # lint with ruff, auto-fixing what it can
make clean      # remove the venv and other generated files
```

`make run` is equivalent to running `uv run python extract_graphics.py` directly.

Tkinter is required and ships with most Python installations, but isn't something `uv`/`pip` can install - see "Packages and dependencies" below if `import tkinter` fails.

This application works on Windows, Linux and macOS.

### GUI

![Graphical User Interface](https://github.com/novalic/extract_nes_graphics/blob/master/images/ss.png)

The GUI is simple. There's only 4 buttons:
- ***Dump file*** Let's you browse your computer for a single .nes or .chr file and loads it into the program.
- ***Dump folder*** It also let you browse through your file system to define a directory. 

After selecting one of the these options the following two buttons become functional:

- ***Save to...*** This lets you choose a destination folder for files processing. If none is specified, output files will be saved in the same folder as the input files. It is highly recommended to use this option when using the folder dump.
- ***Go*** This button puts everything to work. For a single file it's really quick and easy. Processing of a large amount of files will not be very fast due to the open/close operations for each file and all the data processing. I haven't found any bugs yet, but the program fails with broken files. This is handled internally and the program doesn't crash. When processing large amounts of files, you would want to know which files were broken, and an important and powerful feature this tool includes is the LOGFILE generation. Whenever you perform a folder dump a file named LOG.TXT is saved inside the input folder, containing a summary of the execution. This summary includes the names of the files that have failed. Here you can see the format of these log files:

```
EXECUTION COMPLETE.
Started: 10/14/17 - 14:33:17
Finished: 10/14/17 - 14:52:43
________________________________________________
Total files processed: 2
Successfully converted: 1
Not converted (ERROR): 1
________________________________________________
Unfinished_graphics.chr
________________________________________________
```

The output image dimensions is set internally and tries to build an image with reasonable proportions.

- ***Exit*** No need to explain what this button does.


There's also a status bar that usually indicates what are your next steps to follow.

### Project layout

The implementation lives under `src/extract_nes_graphics/`:

- `decoder.py` - pure CHR-bytes-to-pixel-matrix decoding (no file/GUI side effects).
- `ines.py` - parses the iNES `.nes` header to locate and extract the embedded CHR ROM bank.
- `png_writer.py` - writes a decoded pixel matrix out as a `.png`.
- `conversion_log.py` - builds/writes the `LOG.TXT` summary of a folder dump.
- `batch.py` - non-GUI orchestration (single file / whole folder), used by both the GUI and the test suite.
- `gui.py` - the Tkinter UI, which delegates all of the above.

`extract_graphics.py` at the repo root is kept as a thin, backwards-compatible entry point. Tests live in `tests/`, one file per module above, with 100% coverage.

## Packages and dependencies

- ***Python >= 3.10***
- ***[uv](https://docs.astral.sh/uv/)*** Used to manage the virtual environment and dependencies (see `pyproject.toml` / `uv.lock`).
- ***pypng*** Great .png image manipulation package. Simple and quick to understand.
- ***numpy*** Used to vectorize CHR tile decoding.
- ***Tkinter*** A really simple and powerful package to build GUIs quickly. It's part of the Python standard library, not an installable dependency, but it does need to be available in whichever Python you use:
  - On Linux, if `import tkinter` fails, install your distro's `python3-tk` package.
  - On macOS, the system's bundled Tk is old and deprecated (and lacks proper PNG support); if you hit `TclError`s, install a modern Tcl/Tk (`brew install tcl-tk`) and build/select a Python that links against it (e.g. via `pyenv install --force` with `PYTHON_CONFIGURE_OPTS` pointing at it).
- Dev-only: ***pytest***, ***coverage*** and ***ruff*** (linting), installed via `make install`.

## To do

- Might add executables for Windows and Linux using [Packer](https://github.com/hashicorp/packer).
- A HELP screen might be implemented inside the program some day.
