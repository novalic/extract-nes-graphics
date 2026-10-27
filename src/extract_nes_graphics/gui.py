"""Tkinter GUI for the CHR/NES to PNG converter."""
import os
import time
from tkinter import Tk, Frame, Label, Button, TOP, BOTTOM, \
                    DISABLED, NORMAL, BOTH, PhotoImage, Canvas, StringVar
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

from extract_nes_graphics.batch import convert_single_file, is_convertible

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
from extract_nes_graphics.conversion_log import write_log


class ChrToPng(Tk):
    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        # menu left
        self.clearVars()
        self.frame_w = Frame(self, width=100, bg="black")
        self.frame_w2 = Frame(self.frame_w, width=100, height=150, bg='#dfdfdf')

        self.left_title = Label(self.frame_w2, text='', bg='#dfdfdf')
        self.left_title.pack()
        self.s_title = Label(self.frame_w2, text='# @_#E', bg='#dfdfdf')
        self.s_title.pack(side=BOTTOM)

        self.but_file = Button(self.frame_w2, text='Dump file', command=self.getPath)
        self.but_fold = Button(self.frame_w2, text='Dump folder', command=self.getPathDir)
        self.but_sdir = Button(self.frame_w2, state=DISABLED, text='Save to...', command=self.setDirectory)
        self.but_conv = Button(self.frame_w2, state=DISABLED, text='Go', command=self.convertFile)
        self.but_exit = Button(self.frame_w2, text='Exit', command=lambda: exit())
        self.but_file.pack(fill=BOTH)
        self.but_fold.pack(fill=BOTH)
        self.but_sdir.pack(fill=BOTH)
        self.but_conv.pack(fill=BOTH)
        self.but_exit.pack(fill=BOTH, side=BOTTOM)
        famicom_img = PhotoImage(file=os.path.join(IMAGES_DIR, 'img.png'))
        famicom_label = Label(self.frame_w2, image=famicom_img)
        famicom_label.image = famicom_img
        famicom_label.pack(fill=BOTH, expand=True)
        self.frame_w2.pack(side=TOP, fill=BOTH, expand=True)

        # right area
        self.frame_e = Frame(self, bg="#dfdfdf")

        self.some_title = Label(self.frame_e, text="__ by nnov 2017 __  vaporw8bit  ___", bg="#dfdfdf")
        self.some_title.pack()
        self.canvas_area = Canvas(self, width=500, height=400, background="#ffffff")
        self.canvas_area.grid(row=1, column=1)

        back_img = PhotoImage(file=os.path.join(IMAGES_DIR, 'back.png'))
        back_label = Label(self.canvas_area, image=back_img)
        back_label.image = back_img
        back_label.pack(fill=BOTH, expand=True)

        # status
        self.status_frame = Frame(self)
        self.labelVariable = StringVar()
        self.status = Label(self.status_frame, textvariable=self.labelVariable, anchor="w", fg="white", bg="purple")
        self.status.pack(fill=BOTH, expand=True)
        self.labelVariable.set('Please select a CHR file.')

        self.frame_w.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.frame_e.grid(row=0, column=1, sticky="ew")
        self.canvas_area.grid(row=1, column=1, sticky="nsew")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.resizable(False, False)

    def clearVars(self):
        self.save_dir = ''
        self.filename = ''

    def configOptions(self, enable_disable):
        if enable_disable:
            self.but_sdir['state'] = NORMAL
            self.but_conv['state'] = NORMAL
        else:
            self.but_sdir['state'] = DISABLED
            self.but_conv['state'] = DISABLED

    def getPath(self):
        self.filename = askopenfilename(filetypes=[('All files', '*'), ('CHR files', '*.chr'), ('NES files', '*.nes')])
        if self.filename:
            self.labelVariable.set(os.path.split(self.filename)[1] + ' selected.')
            self.save_dir = os.path.split(self.filename)[0]
            self.configOptions(True)

    def getPathDir(self):
        self.filename = askdirectory()
        if self.filename:
            self.save_dir = self.filename
            self.labelVariable.set('".../' + self.filename.split('/')[-1] + '" directory selected.')
            self.configOptions(True)

    def setDirectory(self):
        self.save_dir = askdirectory()

    def convertFile(self):
        self.configOptions(False)
        if self.filename == '':
            self.labelVariable.set('Please enter a valid file or directory.')
        if not is_convertible(self.filename):
            dump_dir = self.filename
            good_files = 0
            bad_files = 0
            list_bad_files = ''
            starting_at = time.strftime('%x - %X')
            self.labelVariable.set('Processing files.')

            for a_file in sorted(x for x in os.listdir(self.filename) if is_convertible(x)):
                self.filename = dump_dir + '/' + a_file
                try:
                    convert_single_file(self.filename, self.save_dir)
                    good_files += 1
                except Exception:
                    bad_files += 1
                    list_bad_files += '@@' + a_file
                self.labelVariable.set(str(good_files + bad_files) + ' files processed. See LOG.TXT for info.')
                # Without this, Tkinter only repaints the status label (and
                # responds to window-manager events like move/resize) once
                # the whole batch finishes, so a folder dump looks frozen
                # for its entire duration instead of showing live progress.
                self.update_idletasks()

            # Written once at the end rather than after every file: re-opening
            # and rewriting LOG.TXT from scratch on every iteration is wasted
            # I/O that scales with the number of files in the folder.
            write_log(dump_dir, good_files, bad_files, list_bad_files, starting_at, time.strftime('%x - %X'))
        else:
            try:
                convert_single_file(self.filename, self.save_dir)
                self.labelVariable.set(os.path.split(self.filename)[1] + ' was converted successfully.')
            except Exception:
                self.labelVariable.set('There was an error while processing ' + os.path.split(self.filename)[1] + '.')
        self.clearVars()
        self.configOptions(True)


def main():
    gui = ChrToPng(None)
    gui.title('NES & FC CHR to PNG')
    gui.geometry('400x300')
    gui.filename = 'No CHR file selected.'
    gui.mainloop()
