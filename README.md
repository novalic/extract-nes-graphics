# CHR to PNG

This is a basic tool to convert .nes or .chr files to a .png image. There might be some similar tools around the web, but I've been looking for one for quite some time and couldn't find one that worked neither on Linux or 64bit Windows. It was a really nice thing to do and it's part of some research I have been doing lately about he NES architecture. Also I included a nice and simple GUI.

## Some documentation

### Usage

There's no executables for now, just running:
```Python
python extract_graphics.py
```
will do the job. Please note that if Python 3 is not your default, you might have to run it as python3 ... .This application works both on Windows and Linux.


### GUI

![Graphical User Interface](https://github.com/novalic/nes8bit/blob/master/t_extract_graphics/images/ss.png)

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

## Packages and dependencies

- ***Python=3.5***
- ***pypng=0.0.18*** Great .png image manipulation package. Simple and quick to understand.
- ***numpy=1.13.3*** Some complex operations become really simple.
- ***Tkinter*** A really simple and powerful package to build GUIs quickly.

## To do

- Might add executables for Windows and Linux.
- A HELP screen will be implemented inside the program some day.
