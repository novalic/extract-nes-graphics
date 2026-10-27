"""Tests for extract_nes_graphics.gui (Tkinter UI).

tests/conftest.py installs a fake tkinter when the real bindings aren't
available, so these tests exercise ChrToPng's logic (state handling,
delegating to batch.py) without actually rendering a window.
"""
from unittest.mock import MagicMock

import pytest

from extract_nes_graphics.gui import DISABLED, NORMAL, ChrToPng

VALID_CHR_BYTES = bytes(128 * 16)


@pytest.fixture
def gui():
    return ChrToPng(None)


class TestForceLightAppearance:
    def test_calls_the_macos_appearance_tcl_command(self, monkeypatch):
        fake_tk = MagicMock()
        monkeypatch.setattr(ChrToPng, 'tk', fake_tk, raising=False)

        gui = ChrToPng(None)

        fake_tk.call.assert_any_call('::tk::unsupported::MacWindowStyle', 'appearance', gui, 'aqua')

    def test_swallows_errors_on_platforms_without_the_command(self, monkeypatch):
        bad_tk = MagicMock()
        bad_tk.call.side_effect = Exception('not supported here')
        monkeypatch.setattr(ChrToPng, 'tk', bad_tk, raising=False)

        gui = ChrToPng(None)  # must not raise

        assert gui.labelVariable.get() == 'Please select a CHR file.'


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

    def test_enable_sets_buttons_to_normal(self, gui):
        gui.configOptions(True)
        gui.but_sdir.__setitem__.assert_called_with('state', NORMAL)
        gui.but_conv.__setitem__.assert_called_with('state', NORMAL)


class TestGetPath:
    def test_selecting_a_file_sets_state_and_enables_buttons(self, gui, monkeypatch, tmp_path):
        chosen = str(tmp_path / 'sprites.chr')
        monkeypatch.setattr('extract_nes_graphics.gui.askopenfilename', lambda **kwargs: chosen)

        gui.getPath()

        assert gui.filename == chosen
        assert gui.save_dir == str(tmp_path)
        assert gui.labelVariable.get() == 'sprites.chr selected.'
        gui.but_conv.__setitem__.assert_called_with('state', NORMAL)

    def test_cancelling_the_dialog_leaves_state_untouched(self, gui, monkeypatch):
        monkeypatch.setattr('extract_nes_graphics.gui.askopenfilename', lambda **kwargs: '')

        gui.getPath()

        assert gui.filename == ''
        assert gui.save_dir == ''


class TestGetPathDir:
    def test_selecting_a_folder_sets_state_and_enables_buttons(self, gui, monkeypatch, tmp_path):
        monkeypatch.setattr('extract_nes_graphics.gui.askdirectory', lambda **kwargs: str(tmp_path))

        gui.getPathDir()

        assert gui.filename == str(tmp_path)
        assert gui.save_dir == str(tmp_path)
        gui.but_conv.__setitem__.assert_called_with('state', NORMAL)

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
    def test_single_file_success(self, gui, tmp_path):
        chr_file = tmp_path / 'sprites.chr'
        chr_file.write_bytes(VALID_CHR_BYTES)
        gui.filename = str(chr_file)
        gui.save_dir = str(tmp_path)

        gui.convertFile()

        assert (tmp_path / 'sprites.chr.png').exists()
        assert gui.labelVariable.get() == 'sprites.chr was converted successfully.'
        # convertFile clears state and re-enables the buttons when it's done.
        assert gui.filename == ''
        gui.but_conv.__setitem__.assert_called_with('state', NORMAL)

    def test_single_file_failure_sets_error_message(self, gui, tmp_path):
        gui.filename = str(tmp_path / 'missing.chr')
        gui.save_dir = str(tmp_path)

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

    def test_folder_dump_converts_each_file(self, gui, tmp_path):
        (tmp_path / 'good.chr').write_bytes(VALID_CHR_BYTES)
        (tmp_path / 'bad.chr').write_bytes(bytes(20))  # truncated tile, will fail
        gui.filename = str(tmp_path)
        gui.save_dir = str(tmp_path)

        gui.convertFile()

        assert (tmp_path / 'good.chr.png').exists()
        assert (tmp_path / 'LOG.TXT').exists()
        assert 'Not converted (ERROR): 1' in (tmp_path / 'LOG.TXT').read_text()
        assert gui.labelVariable.get() == '2 files processed. See LOG.TXT for info.'

    def test_folder_dump_keeps_the_ui_responsive_between_files(self, gui, tmp_path, monkeypatch):
        (tmp_path / 'a.chr').write_bytes(VALID_CHR_BYTES)
        (tmp_path / 'b.chr').write_bytes(VALID_CHR_BYTES)
        gui.filename = str(tmp_path)
        gui.save_dir = str(tmp_path)
        update_idletasks = MagicMock()
        monkeypatch.setattr(gui, 'update_idletasks', update_idletasks)

        gui.convertFile()

        assert update_idletasks.call_count == 2


class TestMain:
    def test_builds_and_runs_the_app(self):
        from extract_nes_graphics import gui as gui_module

        gui_module.main()
