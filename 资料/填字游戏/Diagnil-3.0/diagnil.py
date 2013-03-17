#! /usr/bin/env python

#  Diagnil: Diagramless Crossword Assistant
#      A utility for solving diagramless puzzles interactively
#  Author          : Ben Di Vito <bdivito@cox.net>
#  Created On      : 12 Jan 2002
#  Last Modified On: 04 Aug 2012
#  Status          : Stable
#  Version         : 3.0
#
#  Copyright (c) 2003-2012, Ben Di Vito.
#
#  This is open source software, distributed under a BSD-style license.
#  See the accompanying file 'License' for details.
#
#  See Help text (user's guide) for a description of features.
#  Requires Python version >= 2.6
#  Configured for and tested on Linux, Windows, OS x.
#  Runs best at resolution 1024x768 or higher.
#

import os, sys

# The following startup scheme includes a workaround for the buggy Tcl/Tk
# version found in /System/Library/Frameworks on OS X.  Users can upgrade to
# a newer version that goes in /Library/Frameworks.  This version, however,
# will fail to load under Python 2.6 or later because its search order
# places /System/Library/Frameworks first.  In this case, we set a suitable
# environment variable to elevate /Library/Frameworks to the first position.
# A new Python process is then forked to load and start Diagnil.  Otherwise,
# the load and startup action is caused by module importing.

if sys.platform == 'darwin' and sys.version_info[:2] > (2, 5):
    os.environ['DYLD_FRAMEWORK_PATH'] = \
        '/Library/Frameworks:/System/Library/Frameworks'
    if sys.argv[0]:
        base_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        base_directory = os.getcwd()
    os.system('cd %s; python diag_load.py &' % base_directory)
#    os.system('python diag_load.py&')
else:
    # normal startup
    import diag_load
    # doesn't return until application quits
