"""Tests for the top-level extract_nes_graphics.main() wrapper."""


class TestMain:
    def test_delegates_to_gui_main(self, monkeypatch):
        import extract_nes_graphics
        from extract_nes_graphics import gui

        called = []
        monkeypatch.setattr(gui, 'main', lambda: called.append(True))

        extract_nes_graphics.main()

        assert called == [True]
