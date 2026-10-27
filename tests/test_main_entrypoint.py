"""Tests for the `python -m extract_nes_graphics` entry point."""
import runpy


class TestMainEntrypoint:
    def test_running_as_main_calls_gui_main(self, monkeypatch):
        from extract_nes_graphics import gui

        called = []
        monkeypatch.setattr(gui, 'main', lambda: called.append(True))

        runpy.run_module('extract_nes_graphics.__main__', run_name='__main__')

        assert called == [True]
