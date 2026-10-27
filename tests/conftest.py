"""Shared pytest fixtures/setup.

gui.py is Tkinter UI code: creating a real ChrToPng() spins up an actual Tk
window and asks the real Tk to decode the real image files. That makes
tests dependent on things that have nothing to do with the logic being
tested - a display/window system being available, and the installed Tk
build's image codecs being able to read a given PNG (which can and does
fail depending on the platform's Tk build, independent of any bug in this
code).

So regardless of whether a real tkinter is importable, we install a
minimal fake in sys.modules before gui.py is ever imported. This lets tests
exercise ChrToPng's actual logic (clearVars, configOptions, convertFile,
...) without ever creating a real window or touching a real image decoder.
"""
import sys
import types
from unittest.mock import MagicMock


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
for const_name in ('TOP', 'BOTTOM', 'DISABLED', 'NORMAL', 'BOTH'):
    setattr(fake_tkinter, const_name, const_name)

fake_filedialog = types.ModuleType('tkinter.filedialog')
fake_filedialog.askopenfilename = MagicMock(name='askopenfilename')
fake_filedialog.askdirectory = MagicMock(name='askdirectory')
fake_tkinter.filedialog = fake_filedialog

sys.modules['tkinter'] = fake_tkinter
sys.modules['tkinter.filedialog'] = fake_filedialog
