
Diagnil: Diagramless Crossword Assistant

Version 3.0  ---  Released  4 August 2012  ---  Requires Python >= 2.6

http://blueherons.org/diagnil/

Contact: Ben Di Vito  <bdivito@cox.net>


------------------------

Diagnil is a software application to help solvers of diagramless
crossword puzzles. It supports the process of solving puzzles
distributed in print form and those distributed electronically in the
Across Lite or Crossword Solver file format.


1. Background

The diagramless puzzle is a crossword variant where only word clues
are provided; word locations are not disclosed.  (If a grid is
supplied, it is completely blank.)  Solving a diagramless puzzle
requires not only determining the words but also where they lie on the
grid.

Despite the ubiquity of standard crosswords, the diagramless variety
remains much less popular.  One plausible reason for this is that
diagramless puzzles are viewed as too difficult.  Though not
suitable for beginners, they are easier to solve than is often
presumed.

A second, more justifiable reason is that their solving mechanics can
be tedious, especially when working on paper.  Although the
intellectual challenge of diagramless puzzles is appealing, the need
to frequently redraw to converge on the correct word layout can sap
the enjoyment from what should be recreation.  While brilliant solvers
are undaunted, mere mortals wear out their erasers.

Diagnil is a software tool designed to remove much of the tedium and
make diagramless solving practical and enjoyable for most crossword
enthusiasts.  Software applications for crosswords are readily
available, of course.  Some have addressed the diagramless variant,
albeit in a superficial way.  If you have tried such tools and found
them wanting, you might find Diagnil's style of operation more to your
liking.  Diagnil departs from those other tools by being optimized for
one task: it's all diagramless, all the time.

In a nutshell, you solve puzzles using Diagnil by entering words,
placing them on a grid, and moving them around until the final shape
is achieved.  All you need to begin are lists of word clues obtained
from books, newspapers, or puzzle files obtained from online sources.
Puzzles as large as those published in Sunday newspapers (typically up
to 21 by 21) are accommodated easily.


2. Release Information


Current version: 3.0, released  4 August 2012

Author: Ben Di Vito  <bdivito@cox.net>

Requires: Python 2.6 or later (included in Windows installer)

Caveats: best with screen resolution of 1024x768 or higher
         best with multi-button mouse (Mac users)

Terms of use: open-source software, free to use and redistribute
(BSD-style license in accompanying file)


3. Installation and Setup

3.1 Microsoft Windows

The fully self-contained Windows installer includes everything
(the application program plus all supporting software).

 1. Download the appropriate installer file from the download page to
    the desktop or a folder of your choice.

 2. This executable setup file can be launched in the usual ways on
    Windows, e.g., double clicking its icon.  With most versions of
    Windows (NT/2000/XP/Vista/Win7), you will likely need
    "administrative privilege" to install in the default folders.
    This means you will need to be running under, or need to switch
    to, an "owner" or "administrator" account. With more recent
    editions (Vista and Windows 7), you might simply be asked for your
    permission to proceed.

 3. After the setup program starts, it will prompt you through the
    installation process.  Afterwards you will have a desktop shortcut
    and a start menu item for launching Diagnil.


3.2 Mac OS X

If you have the Tiger, (Snow) Leopard or Lion versions of OS X
(10.4+), the disk image file contains a pre-configured, application
suitable for immediate use under OS X.

 1. Choose the file from the download page that matches your processor
    family, either Intel or PowerPC.  Most people will need Intel; all
    Macs made after 2006 have Intel processors.  If unsure of the type,
    select the Apple logo on the menu bar (left-most item) and look
    under "About This Mac".

 2. Download the disk image file you selected.  Your browser will
    either open the disk image or save it to a folder of your choice.
    It has the name 'Diagnil-3.0-intel.dmg' or
    'Diagnil-3.0-power.dmg'.

 3. If the 'dmg' file was saved, double-click its icon to open it.  If
    you want to try the Diagnil application before installing, simply
    double-click its icon.  If you decide to install it, drag its icon
    to the Applications folder.  You might need to have access to an
    Administrator password for this step.

 4. Alternatively, you can copy the application contained in the disk
    image to another folder or to your desktop.  Wherever it is
    located, you will now have a ready-to-run universal application
    for OS X.


3.3 Linux

Most recent versions of Linux can run Diagnil out of the box.

 1. Download the tar archive file from the download page.  It has the
    name 'Diagnil-3.0.tgz'.

 2. Unpack the distribution using the shell command 
    'tar xzf <path>/Diagnil-3.0.tgz' in a directory of your choice.
    The subdirectory Diagnil-3.0 will be created.

 3. You may now start using Diagnil from a shell via the command
    '<path>/Diagnil-3.0/diagnil.py'.  This file is an executable script.

 4. If you prefer, you can create a shortcut or launcher icon for
    starting the application.  Use '<path>/Diagnil-3.0/diagnil.py'
    as the startup command.  If this command fails, try
    'python <path>/Diagnil-3.0/diagnil.py' instead.


4. Using the Source Code Distribution

The following instructions are for technically oriented users who wish
to use or experiment with the source code.

 1. Diagnil is written in the Python programming language and requires
    a run-time environment. This includes the Tkinter component, which
    is a Python library providing access to the Tcl/Tk graphical user
    interface (GUI) services.

 2. Windows systems normally lack Python and the supporting packages;
    see the Python download page (http://www.python.org/download/) to
    retrieve them. Tkinter and Tcl/Tk come bundled with the Windows
    Python distribution.

 3. As of version 10.4 (Tiger), OS X comes with Python and Tkinter
    already installed as well as an Aqua version of Tcl/Tk.
    Nevertheless, OS X users might want to download a fresh version of
    Tcl/Tk (http://www.activestate.com/activetcl/downloads/) to get
    the latest bug fixes.  One known problem is poor behavior with
    mouse wheels and touchpads.  If you experience such problems and
    find them objectionable, you can download a newer version.  Choose
    a version in the 8.4 series newer than 8.4.13 or one in the 8.5
    series.

 4. Python is included in most Linux and Unix distributions.  Some
    Linux distributions include Python but not the Tkinter package or
    the Tcl/Tk package it requires.  These are usually available and
    easily obtained through your system-specific package retrieval
    mechanism.

 5. If you need to download Python, note that Diagnil requires a
    version in the 2.x series (at least 2.6). It will not work with
    the newer 3.x versions of Python.  As of December 2010, version
    2.7 was the latest and most suitable version to retrieve.

 6. To install and run Diagnil, download and unpack one of the source
    archive files from the table above.  It will create a directory
    called Diagnil-3.0.

 7. You may now start using Diagnil from a shell or other application
    launching mechanism. No build or compilation phase is required.
    Simply invoke the command '<path>/Diagnil-3.0/diagnil.py' or its
    functional equivalent.

 8. If this command fails, or you want to use a different version of
    Python, try 'python <path>/Diagnil-3.0/diagnil.py' instead.


5. Package Files

README.txt               Summary of distribution (this file)
License.txt              Terms of use
diagnil.py               Main Diagnil program (Python source)
diag_mmmm.py             Diagnil module files (Python source)
samples                  Subdirectory of sample puzzle files
images                   Subdirectory of images for help information
settings_ppp.py          User preferences
tile_dialogs.tcl         Alternative tk_messageBox dialogs
diagnil.gif/.ico/.icns   Application icons
Design_notes.txt         Notes for software developers


6. Final Remarks

This program is likely to undergo further development, but it should
meet most users' needs as is.  Additional refinements will make it
more useful to a broader array of crossword enthusiasts.  Feedback of
any kind is encouraged so that it might be improved.


7. Acknowledgments

Diagnil is written in the Python programming language and uses its
run-time system, including the Tkinter package to access the Tcl/Tk
graphical user interface.  Thanks go to Guido van Rossum and many
contributors for developing the excellent Python tools.  Equally
significant are the contributions of John Ousterhout and many, many
others for developing the Tcl/Tk GUI package on which Tkinter is
based.  The Tile/ttk extensions to Tk developed by Joe English are
used as well.

Thomas Heller wrote the py2exe tool for constructing binary Windows
distributions from Python programs.  Jordan Russell developed the Inno
Setup application for creating executable Windows installers.  Bob
Ippolito developed the py2app tool for creating Mac OS X application
bundles.

Much of the .puz file parsing code is based on the file format
documentation compiled by Josh Myer, with additional contributions by
Evan Martin, Chris Casinghino, Michael Greenberg and Alex Boisvert.
The scrambling algorithm details were provided by Mike Richards.

The MultiListbox class is an adaptation and extension of this idea:
  Recipe 52266: MultiListbox Tkinter widget (Python) by Brent Burley
  http://code.activestate.com/recipes/52266-multilistbox-tkinter-widget/
