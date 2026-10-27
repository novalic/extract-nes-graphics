"""Shared pytest fixtures/setup.

gui.py needs tkinter, which may not have its native Tcl/Tk bindings
installed in every environment (e.g. headless CI). When the real tkinter
can't be imported, we install a minimal fake in sys.modules so gui.py can
still be imported and its non-rendering logic (clearVars, configOptions,
convertFile, ...) exercised by tests.
"""
import sys
import types
from unittest.mock import MagicMock

try:
    import tkinter  # noqa: F401
    import tkinter.filedialog  # noqa: F401
except ModuleNotFoundError:
    class _FakeStringVar:
        def __init__(self, *args, **kwargs):
            self._value = ''

        def set(self, value):
            self._value = value

        def get(self):
            return self._value

    class _FakeTk:
        """Stands in for tkinter.Tk as a real class so ChrToPng can subclass it."""

        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, name):
            # title(), geometry(), mainloop(), grid_rowconfigure(), etc.
            return MagicMock(name=name)

    fake_tkinter = types.ModuleType('tkinter')
    fake_tkinter.Tk = _FakeTk
    fake_tkinter.StringVar = _FakeStringVar
    for widget_name in ('Frame', 'Label', 'Button', 'Canvas', 'PhotoImage'):
        setattr(fake_tkinter, widget_name, MagicMock(name=widget_name))
    for const_name in ('TOP', 'BOTTOM', 'DISABLED', 'BOTH'):
        setattr(fake_tkinter, const_name, const_name)

    fake_filedialog = types.ModuleType('tkinter.filedialog')
    fake_filedialog.askopenfilename = MagicMock(name='askopenfilename')
    fake_filedialog.askdirectory = MagicMock(name='askdirectory')
    fake_tkinter.filedialog = fake_filedialog

    sys.modules['tkinter'] = fake_tkinter
    sys.modules['tkinter.filedialog'] = fake_filedialog
