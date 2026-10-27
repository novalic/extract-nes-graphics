"""Tests for extract_nes_graphics.gui (Tkinter UI).

tests/conftest.py installs a fake tkinter when the real bindings aren't
available, so these tests exercise ChrToPng's logic (state handling,
delegating to batch.py) without actually rendering a window.

Several tests here intentionally expect a NameError: `configOptions(True)`
references the undefined name `NORMAL` (a pre-existing bug), which this
suite documents rather than papers over. It is fixed, and these tests
updated, in a later commit.
"""
import pytest

from extract_nes_graphics.gui import ChrToPng, DISABLED

VALID_CHR_BYTES = bytes(128 * 16)


@pytest.fixture
def gui():
    return ChrToPng(None)


class TestInitialize:
    def test_sets_default_status_message(self, gui):
        assert gui.labelVariable.get() == 'Please select a CHR file.'

    def test_clears_filename_and_save_dir(self, gui):
        assert gui.filename == ''
        assert gui.save_dir == ''


class TestClearVars:
    def test_resets_filename_and_save_dir(self, gui):
        gui.filename = 'something.chr'
        gui.save_dir = '/some/dir'

        gui.clearVars()

        assert gui.filename == ''
        assert gui.save_dir == ''


class TestConfigOptions:
    def test_disable_sets_buttons_to_disabled(self, gui):
        gui.configOptions(False)
        gui.but_sdir.__setitem__.assert_called_with('state', DISABLED)
        gui.but_conv.__setitem__.assert_called_with('state', DISABLED)

    def test_enable_raises_due_to_undefined_normal(self, gui):
        # Known bug: NORMAL is never imported from tkinter.
        with pytest.raises(NameError):
            gui.configOptions(True)


class TestGetPath:
    def test_selecting_a_file_sets_state_then_crashes_on_enable(self, gui, monkeypatch, tmp_path):
        chosen = str(tmp_path / 'sprites.chr')
        monkeypatch.setattr('extract_nes_graphics.gui.askopenfilename', lambda **kwargs: chosen)

        with pytest.raises(NameError):
            gui.getPath()

        assert gui.filename == chosen
        assert gui.save_dir == str(tmp_path)
        assert gui.labelVariable.get() == 'sprites.chr selected.'

    def test_cancelling_the_dialog_leaves_state_untouched(self, gui, monkeypatch):
        monkeypatch.setattr('extract_nes_graphics.gui.askopenfilename', lambda **kwargs: '')

        gui.getPath()

        assert gui.filename == ''
        assert gui.save_dir == ''


class TestGetPathDir:
    def test_selecting_a_folder_sets_state_then_crashes_on_enable(self, gui, monkeypatch, tmp_path):
        monkeypatch.setattr('extract_nes_graphics.gui.askdirectory', lambda **kwargs: str(tmp_path))

        with pytest.raises(NameError):
            gui.getPathDir()

        assert gui.filename == str(tmp_path)
        assert gui.save_dir == str(tmp_path)

    def test_cancelling_the_dialog_leaves_state_untouched(self, gui, monkeypatch):
        monkeypatch.setattr('extract_nes_graphics.gui.askdirectory', lambda **kwargs: '')

        gui.getPathDir()

        assert gui.filename == ''
        assert gui.save_dir == ''


class TestSetDirectory:
    def test_sets_save_dir_from_the_dialog(self, gui, monkeypatch, tmp_path):
        monkeypatch.setattr('extract_nes_graphics.gui.askdirectory', lambda **kwargs: str(tmp_path))

        gui.setDirectory()

        assert gui.save_dir == str(tmp_path)


class TestConvertFile:
    def test_single_file_success_converts_then_crashes_on_enable(self, gui, tmp_path):
        chr_file = tmp_path / 'sprites.chr'
        chr_file.write_bytes(VALID_CHR_BYTES)
        gui.filename = str(chr_file)
        gui.save_dir = str(tmp_path)

        with pytest.raises(NameError):
            gui.convertFile()

        assert (tmp_path / 'sprites.chr.png').exists()
        assert gui.labelVariable.get() == 'sprites.chr was converted successfully.'

    def test_single_file_failure_sets_error_message_then_crashes_on_enable(self, gui, tmp_path):
        gui.filename = str(tmp_path / 'missing.chr')
        gui.save_dir = str(tmp_path)

        with pytest.raises(NameError):
            gui.convertFile()

        assert gui.labelVariable.get() == 'There was an error while processing missing.chr.'

    def test_empty_filename_is_treated_as_a_folder_dump(self, gui, tmp_path):
        # Known bug: an empty filename sets the 'enter a valid file'
        # message, but execution falls through into the folder-dump branch
        # anyway (since '' isn't convertible), immediately overwriting it.
        gui.filename = ''
        gui.save_dir = str(tmp_path)

        with pytest.raises(FileNotFoundError):
            gui.convertFile()

        assert gui.labelVariable.get() == 'Processing files.'

    def test_folder_dump_converts_each_file_then_crashes_on_enable(self, gui, tmp_path):
        (tmp_path / 'good.chr').write_bytes(VALID_CHR_BYTES)
        (tmp_path / 'bad.chr').write_bytes(bytes(16))
        gui.filename = str(tmp_path)
        gui.save_dir = str(tmp_path)

        with pytest.raises(NameError):
            gui.convertFile()

        assert (tmp_path / 'good.chr.png').exists()
        assert (tmp_path / 'LOG.TXT').exists()
        assert 'Not converted (ERROR): 1' in (tmp_path / 'LOG.TXT').read_text()


class TestMain:
    def test_builds_and_runs_the_app(self):
        from extract_nes_graphics import gui as gui_module

        gui_module.main()
