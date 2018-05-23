import binascii
import numpy
import png
import os
import time
from tkinter import Tk, Frame, Label, Button, TOP, BOTTOM, \
                    DISABLED, BOTH, PhotoImage, Canvas, StringVar
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory


PALETTE = [(0,0,0), (255,0,0), (0,0,255), (255,255,255)]


class chr_to_png(Tk):
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
    self.but_exit = Button(self.frame_w2, text='Exit', command=lambda:exit())
    self.but_file.pack(fill=BOTH)
    self.but_fold.pack(fill=BOTH)
    self.but_sdir.pack(fill=BOTH)
    self.but_conv.pack(fill=BOTH)
    self.but_exit.pack(fill=BOTH, side=BOTTOM)
    famicom_img = PhotoImage(file = 'images/img.png')
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

    back_img = PhotoImage(file = 'images/back.png')
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

    self.resizable(False,False)

  def createLog(self, dump_dir, num_good, num_bad, bad_files, date_start, date_end):
    with open(dump_dir + '/LOG.TXT', 'w') as execution_log:
      execution_log.write('EXECUTION COMPLETE.\n')
      execution_log.write('Started: ' + date_start + '\n')
      execution_log.write('Finished: ' + date_end + '\n')
      execution_log.write('_'*50 + '\n')
      execution_log.write('Total files processed: ' + str(num_good + num_bad) + '\n')
      execution_log.write('Successfully converted: ' + str(num_good) + '\n')
      execution_log.write('Not converted (ERROR): ' + str(num_bad) + '\n')
      execution_log.write('_'*50 + '\n')
      [ execution_log.write(x + '\n') for x in bad_files.split('@@')]
      execution_log.write('_'*50 + '\n')

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
    self.filename = askopenfilename(filetypes=[('All files', '*'), ('CHR files','*.chr'), ('NES files', '*.nes')])
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
    if (self.filename == ''):
      self.labelVariable.set('Please enter a valid file or directory.')
    if not (self.filename.lower().endswith('.chr') or self.filename.lower().endswith('.nes')):
      dump_dir = self.filename
      good_files = 0
      bad_files = 0
      list_bad_files = ''
      starting_at = time.strftime('%x - %X')
      self.labelVariable.set('Processing files.')

      for a_file in sorted([x for x in \
          os.listdir(self.filename) if (x.lower().endswith('.chr') or x.lower().endswith('.nes')) ]):
        self.filename = dump_dir + '/' + a_file
        try:
          self.converter()
          good_files += 1
        except:
          bad_files += 1
          list_bad_files += '@@' + a_file
        self.createLog(dump_dir, good_files, bad_files, list_bad_files, starting_at, time.strftime('%x - %X'))
        self.labelVariable.set(str(good_files + bad_files) + ' files processed. See LOG.TXT for info.')
    else:
      try:
        self.converter()
        self.labelVariable.set(os.path.split(self.filename)[1] + ' was converted successfully.')
      except:
        self.labelVariable.set('There was an error while processing ' + os.path.split(self.filename)[1] + '.')
    self.clearVars();
    self.configOptions(True)

  def converter(self):
    PALETTE = [(0,0,0), (255,0,0), (0,0,255), (255,255,255)]
    TILES_IN_ROW = 128

    with open(self.filename, 'rb') as chr_file:
      in_hex = str(binascii.hexlify(chr_file.read()))[2:-1]

    tiles = [ in_hex[index:index + 32] for index in range(0, len(in_hex), 32) ]
    SIZE_CHR = len(tiles)

    mega_pixel = list();
    IMG_HTILES = int(SIZE_CHR/TILES_IN_ROW)

    row_count = 1
    column_count = 0

    for tile in tiles:
      column_count += 1
      if column_count == 17:
        row_count + 1
        column_count = 1
      decode = [ x + 2*y for x, y in zip(\
                            [int(x) for x in list(bin(int(tile[:16], 16))[2:].zfill(64))], \
                            [int(x) for x in list(bin(int(tile[16:], 16))[2:].zfill(64))] ) ]
      mega_pixel.append([ decode[index:index + 8] for index in range(0, len(decode), 8) ])

    reshape = [ mega_pixel[index:index + IMG_HTILES] for index in range(0, SIZE_CHR, IMG_HTILES) ]

    reshape.append([[[0,0,0,0,0,0,0,0]]*8])

    if len(reshape[-1]) < len(reshape[-2]):
      fill = len(reshape[-2]) - len(reshape[-1])
      [ reshape[-1].append([[0,0,0,0,0,0,0,0]]*8) for i in range(0, fill) ]

    result = [ entry for sublist in \
                [ numpy.hstack(reshape[row]) for row in \
                  range(0, len(reshape)) ] for entry in sublist ]

    png_file = open(self.save_dir + '/' + os.path.split(self.filename)[1] + '.png', 'wb')
    file_writer = png.Writer(len(result[0]), len(result), palette=PALETTE)
    file_writer.write(png_file, result)
    png_file.close()

if __name__ == "__main__":
  gui = chr_to_png(None)
  gui.title('NES & FC CHR to PNG')
  gui.geometry('400x300')
  gui.filename = 'No CHR file selected.'
  gui.mainloop()
