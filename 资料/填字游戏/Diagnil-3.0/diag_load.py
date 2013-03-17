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
#  Configured for and tested on Linux, Windows, OS X.
#  Runs best at resolution 1024x768 or higher.
#


from diag_globals   import *
from diag_util      import *
from diag_classes   import DiagData, PermState
from diag_cmds      import DiagCommands
from diag_events    import DiagEvents
from diag_word_grid import DiagWordGrid
from diag_methods   import DiagMethods


# ---------- Create and start application ---------- #

class Cross(DiagData, DiagEvents, DiagMethods, DiagWordGrid, DiagCommands):
    def __init__(self, master):
        for cl in (DiagData, DiagEvents, DiagMethods,
                   DiagWordGrid, DiagCommands):
            cl.__init__(self, master)

root.title('Diagnil: Diagramless Crossword Assistant')
root.minsize(width=640, height=450)

try:
    cross = Cross(root)
    log_user_message('Diagnil',
                     'New session started.\nSoftware version numbers:\n'
                     '    Diagnil:   %s\n'
                     '    Python:    %s\n'
                     '    Tcl/Tk:     %s' %
                     (version, sys.version.split()[0],
                      root.tk.eval('info patchlevel')))

    # Make key symbols visible when called as a script:
    if __name__ != '__main__':
        sys.modules['__main__'].cross = cross
        sys.modules['__main__'].PermState = PermState
    sys.modules['diag_globals'].cross = cross
    eval_assertion(cross.state_invariant, 'Post-initialization check')

    # if first arg exists, consider it a puzzle file to open
    if len(sys.argv) > 1: cross.open_puz(sys.argv[1])
except:
    trace = StringIO()
    print_exc(100, trace)
    internal_error(trace.getvalue(), 'Initialization')

if user_directory_error:
    user_dialog(showerror, *error_messages['bad_user_directory'])

if preference_load_error:
    user_dialog(showerror, *error_messages['bad_preferences'])

root.mainloop()
