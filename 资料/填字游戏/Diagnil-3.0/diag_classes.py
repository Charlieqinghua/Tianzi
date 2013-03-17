#  Diagnil: Diagramless Crossword Assistant        Version 3.0
#      A utility for solving diagramless puzzles interactively
#
#  Copyright (c) 2003-2012, Ben Di Vito.  <bdivito@cox.net>
#
#  This is open source software, distributed under a BSD-style license.
#  See the accompanying file 'License' for details.
#

from diag_globals   import *
from diag_util      import *


# ---------- Class definitions ---------- #

# Conventions for puzzle classes: 
#   Direction index (dir): 0 = across, 1 = down
#     opposite direction given by 1-dir
#   Only persistent state is stored in puzzle files; the rest is
#     generated during each session.
#   Puzzle file format is one-line version no. string followed by
#     pickled form of PermState object.
#   The 'cells' structure in the AuxState keeps track of word numbers
#     and canvas tags for each cell in each grid.
#   Temporary state is saved in 'temp', 'sess' and 'eph' objects.
#   GUI related state is saved in 'gui' object.

# File format history:
#   Version 0.8     8 Mar 2003      Initial release
#           0.9    18 Oct 2003      Format changed, development version
#           1.0     5 May 2004      Format changed slightly, second release
#                                     - 'final' attribute added; accepts 0.8
#                                       files OK, but blocks less used in 1.0
#           1.2     9 Dec 2006      Format unchanged
#           1.3    13 Mar 2010      Format same with new attributes:
#                                     - 'size_symm' attribute added
#                                     - older formats still accepted
#           2.0     5 Apr 2010      Format same with new attributes:
#                                     - 'puz_defn' attribute added
#           2.1     7 Sep 2010      Format unchanged
#           2.2     3 Jan 2011      Format unchanged
#           2.3    16 Feb 2011      Format same with new attributes:
#                                     - 'alt_words' attribute added
#                                     - 'revealed' attribute added
#           2.4    16 Apr 2011      Format unchanged
#           3.0    29 Oct 2011      Format extended with new attributes:
#                                     - 'solv_time' attribute added
#                                   Added prefix '%Diagnil-' to first line

class PermState(object):          # Persistent state per puzzle
    def __init__(self):
        self.nums    = [[],[]]    # dir -> sorted list of word numbers
        self.words   = [{},{}]    # dir -> {num -> word string (in listbox)}
        self.grid_id = [{},{}]    # dir -> {num -> grid id}
        self.posns   = []         # grid,dir -> {num -> (row,col)}
        self.blocks  = []         # grid -> {(row,col) -> 1}
        for i in range(num_grids):
            self.posns.append([{},{}])   # (word posn on grid)
            self.blocks.append({})       # (block posn on grid)
        self.final   = ()         # finalization status (new in 1.0)
        self.size_symm = ()       # size and symmetry attributes (new in 1.3)
        self.puz_defn = None      # Across Lite .puz file info (new in 2.0)
        self.alt_words = [{},{}]  # dir -> {num -> words string} (new in 2.3)
#        self.revealed = 0        # full solution was revealed (new in 2.3)
#                                 #   added only when needed
        self.solv_time = 0        # solving time (seconds) (new in 3.0)

    def __eq__(self, other):
        return isinstance(other, PermState) and \
               self.nums      == other.nums and \
               self.words     == other.words and \
               self.grid_id   == other.grid_id and \
               self.posns     == other.posns and \
               self.blocks    == other.blocks and \
               self.final     == other.final and \
               self.size_symm == other.size_symm and \
               self.alt_words == other.alt_words
        # puz_defn doesn't change so no need to compare that attribute
        # solv_time changes but not used to compare perm states

    def has_content(self):
        # true if any words or blocks exist; ignores other attributes
        return self.nums[0] or self.nums[1] or \
               filter(None, [ self.blocks[i] for i in range(num_grids) ])


class AuxState(object):           # Auxiliary puzzle state, derived from
    def __init__(self):           # perm state and canvas item numbers;
                                  # recreated on each undo action.
        self.cells = []
        # grid -> [row,col -> [a-letter, d-letter, block]]
        # (both letter fields may have non-None data;
        #  letters and blocks are mutually exclusive)
        # a/d-letter: (num, tags, letter); block: canvas-id
        for i in range(num_grids):
            size = grid_size[i]
            self.cells.append([[[None, None, None] for col in range(size)]
                               for row in range(size)])

class TempState(object):          # Session state per puzzle; initialized
    def __init__(self):           # for each new puzzle in same session
        self.puz_file = ''            # file name of current puzzle
        self.last_saved = None        # perm puzzle state at time last saved
        self.undo_state = []          # perm puzzle states after each step
        self.redo_state = []          # recently undone perm puzzle states
        self.recovery_state = None    # perm puzzle state at start of action
        self.recovery_nonperm = None  # nonperm state at start of action

        self.sel_num_word = [0,0]     # dir -> (num,word,index) of selection
        self.next_word_num = [1,1]    # for autoincrementing word entry
        self.indicator_cur   = [(None,None),(None,None)] # num, index of
                                      # items highlighted in listboxes
        self.indicator_saved = [(None,None),(None,None)]  # items to be restored
        self.multiword_selection = None  # for repeating multiword movements
        self.grid_pattern_up = 0  # display shows grid pattern only
        self.symmetry_mapping = symmetry_mappings['rot']
        self.wrapped_clues =[[],[]]   # cache for listboxes
#        self.url = ''             # when file is downloaded ### future

        self.size_symm = ()       # copy from perm
        self.puz_defn = None      # copy from perm
        self.needs_saving = 0     # importing forces saving
        self.revealed = 0         # full solution was revealed
        self.solv_time = 0        # copy from perm
        self.soln_letter_count = 0  # no. of letter cells (clueful only)

        self.key_cursors = []    # state for key-based navigation
        for i in range(num_grids):
            self.key_cursors.append((0,0,0))   # canvas obj id, row, col

# The following copy selected attributes from perm to temp class instances.
# This is done to omit them from the undoable portion of perm.  These
# attributes need to be copied back to perm when it is saved to a file.

def perm_to_temp(perm, temp):
    temp.size_symm = perm.size_symm
    perm.size_symm = ()
    temp.puz_defn  = perm.puz_defn
    perm.puz_defn  = None
    if getattr(perm, 'revealed', None):
        temp.revealed = perm.revealed
    temp.solv_time = perm.solv_time

def temp_to_perm(temp, perm):
    perm.size_symm = temp.size_symm
    perm.puz_defn  = temp.puz_defn
    # following flag is latched in temp so undo won't erase it
    perm.revealed  = temp.revealed
    perm.solv_time = temp.solv_time


# The puzzle directory for a session starts with the user-preference value.
# The session directory can be changed during file dialogs.  Changes to
# the preference setting don't take effect until the next session.

class SessionState(object):       # Session state for all puzzles;
    def __init__(self, app):      #   initialized only once
        self.current_grid = 0     # which grid set is currently displayed
        self.puzzle_dir = app_prefs['puzzle_folder']   # for file selection
        self.settings_time = \
            os.path.getmtime(os.path.join(user_directory, 'settings.py'))
        self.word_entry_text = ['','']  # to save partial word entries

        # Handler for left click is mode dependent:
        self.next_click_action = app.paste_word
        self.default_click_action = app.paste_word
        self.next_focus = 0       # to toggle entry focus
        self.focus_region = -1    # 0/1: word panel, 2..N: grid, -1: other
        self.quitting = 0         # no. of attempts to exit session
        self.trial_mode = user_trial_mode   # running from dmg file (OS X)

        self.show_boundary = app_prefs['show_boundary']
                                  # show puzzle size boundary
        self.apply_symmetry = app_prefs['apply_symmetry']
                                  # add blocks implied by symmetry
        self.symmetry_type = app_prefs['symmetry_type']
        self.puzzle_width  = app_prefs['puzzle_width']   # optional size
        self.puzzle_height = app_prefs['puzzle_height']
        self.key_navigation = app_prefs['key_navigation']


class EphemeralState(object):     # Short lifetime objects;
    def __init__(self):           #   for commands, mouse motion, etc.
        self.multistep_mode = 0   # for region movement operations
        self.preview = 0          # used during dragging; = 0 on button up,
                                  # = 1 on button down, > 1 on motion
        self.action_done = 1      # 
        self.init_posn = (-1,-1)  # cell on button down event
        self.prev_posn = (-1,-1)  # to track cells during dragging
        self.event_xy = (0,0)     # posn from quiescent motion events
        self.num_word = None      # save (num,word) across preview phase
        self.last_word = [None,None]  # save (num,word) of last entry
        self.init_corners = ()    # ul,lr row,col on button down event
        self.est_cell_num = 0     # estimated word num for current cell (mouse)
        self.est_cell_num_key = 0 # estimated word num for current cell (key)
        self.keep_est_cell_num = 0 # flag for when user increments number
        self.save_est_cell_nums = (0,0) # needed for popup handling

        self.visit_id = 0         # Tk id to cancel cell visit action
        self.key_visit_id = 0     # Tk id to cancel key visit action
        self.scroll_id = 0        # Tk id to cancel listbox scroll action
        self.key_scroll_id = 0    # Tk id to cancel listbox scroll action
        self.preview_id = 0       # Tk id to cancel preview action
        self.popup_id = 0         # Tk id to cancel popup action
        self.timer_id = 0         # Tk id to cancel solving time timer
        self.temp_msg_id = 0      # Tk id to cancel hiding of temp msg panel
        self.solve_time_id = 0    # Tk id to cancel solve time fg change
        self.save_time_id = 0     # Tk id to cancel file save time fg change

        self.start_preview_actions = [] # actions to apply when preview starts
                                        # must accept arg id_to
        self.drag_actions = []    # actions to apply on mouse motion events
        self.drag_words = [[],[]] # row,col,word descriptors for motion events
        self.followup_actions = []# actions to perform after main one completes
        self.dragging_words = []  # descriptors for words dragged in preview
        self.action_string = 'Misc. Action'  # summary for undo/redo messages

        self.last_tick = 0.0      # time of last timer tick
        self.block_toggle = 1     # toggle state for block drawing
        self.warnings = {}        # keys for warning message dictionary
        self.wordbox_posns = [0,0]# tops of wordboxes currently displayed
        self.popup_args = ()      # for right-click menu
        self.popup_posting = 0    # indicates popup menu requested
        self.old_posns = None     # used for region movement operations
        self.old_keys = None      #
        self.old_kc_posn = None   #
        self.wordbox_yview = None # to save over undo/redo: [Ya,Yd]


# ---------- GUI classes and constructor methods ---------- #

class GUI_elements(object):       # GUI objects, including those accessed
                                  #   during session; initialized only once
    def __init__(self, master, app):
        self.master = master
        self.grids = [None]*num_grids         # canvas objects
        self.enter_grid = [None]*num_grids    # window entry actions
        self.leave_grid = [None]*num_grids    # window exit actions
        self.scroll_grid = [None]*num_grids   # 2D scrolling functions
        self.base_tag = [None]*num_grids      # canvas tag of last base gridline
        self.map_grid_posn = [None]*num_grids # event x,y mapping functions
        self.grid_motion_action = [None]*num_grids # cell visit motion handler
        self.create_indicators  = [None]*num_grids # triangle creation function
        self.destroy_indicators = [None]*num_grids # removal function
        self.wheel_action = [None]*(num_grids+2) # mouse wheel handler (Win)

        # triangle objects for row, column tracking:
        self.indicators = [ [None,None] for i in range(num_grids) ]
        if on_aqua: pass           # no separator needed on OS X
        else:
            Frame(master, height=1, bg=block_color, bd=0
                  ).grid(row=0, column=0, sticky='ew')

        # in clueful mode, title, author, copyright line will use rows 1,2
        self.title_line = None
        self.add_work_area(master, app)
        self.app_frame.grid(padx=2, row=3, column=0, sticky='news')
        Frame(master).grid(pady=1, row=4, column=0)

        status_row = Frame(master)    # status line plus puzzle info displays
        if on_aqua:                   # avoid resize handle on lower right
            Frame(status_row).pack(padx=5, side=RIGHT)
        self.save_time_msg, self.puzzle_size, self.solving_time = \
            [ Label(status_row, relief=SUNKEN, bd=1, padx=5)
              for i in range(3) ]
        self.status_line = \
            Label(status_row, anchor=W, relief=SUNKEN, bd=1, padx=5)
        self.status_line2 = \
            Label(status_row, anchor=E, relief=SUNKEN, bd=1, padx=5)

        self.save_time_msg.pack(padx=2, side=RIGHT)
        self.puzzle_size.pack(padx=2, side=RIGHT)
        self.solving_time.pack(padx=2, side=RIGHT)
        self.status_line2.pack(side=RIGHT, padx=2)
        self.status_line.pack(side=LEFT, padx=2, fill=X, expand=YES)
        status_row.grid(padx=5, pady=2, row=5, column=0, sticky='ew')
        master.rowconfigure(3, weight=1, minsize=0)
        master.columnconfigure(0, weight=1, minsize=0)

        self.popup = [None, None]
        self.add_popup_menu(app, 0)
        self.add_popup_menu(app, 1)
        if on_osx:                  # compensate for OS X cursor resets:
            def reset_grid_cursors():
                app.set_grid_cursors(1 - app.sess.next_focus)
                master.update()
            set_user_dialog_cleanup(reset_grid_cursors)
        master.protocol('WM_DELETE_WINDOW', app.exit)
        wrapped_bind(master, '<F1>', display_reporting_procedure, 'reporting')
        if on_osx:
            exit_proc = EventHandler('Key exit', app.exit)
            wrapped_bind(master, '<Command-q>', exit_proc)
            wrapped_bind(master, '<Control-q>', exit_proc)

        # Remove built-in Tab and Shift-Tab bindings and create a
        # virtual event for Shift-Tab.
        master.unbind_all('<Tab>')
        master.event_add('<<ReverseTab>>',
                         *master.event_info('<<PrevWindow>>'))
        master.event_delete('<<PrevWindow>>')

        # Remove Ctrl-y from virtual event Paste
        for e in master.event_info('<<Paste>>'):
            if '-y>' in e or '-Y>' in e :
                master.event_delete('<<Paste>>', e)

        # Following bindings are attached to just one fixed widget of the main
        # window.  This ensures that only one widget triggers the binding and
        # therefore the binding fires only once for each map/unmap event.

        wrapped_bind(status_row, '<Unmap>', 
                     lambda e: app.stop_timer(), 'Unmap app')
        wrapped_bind(status_row, '<Map>',
                     lambda e: app.restart_timer(), 'Map app')

    def configure_title_line(self, title='', author='', copyright=''):
        if self.title_line:
            self.title_line.grid_forget()
            self.title_line.destroy()
            self.title_separator.grid_forget()
            self.title_separator.destroy()
            self.title_line = None
        if title:
            self.title_line = Frame(self.master)
            title_label = Label(self.title_line, text=title, font=bold_font)
            title_label.grid(padx=5, row=0, column=0)
            height = title_label.winfo_reqheight()
            Frame(self.title_line, width=1, height=height,
                  bg=block_color, bd=0).grid(padx=0, row=0, column=1)
            Label(self.title_line, text=author,
                  font=text_font).grid(padx=5, row=0, column=2)
            Frame(self.title_line, width=1, height=height,
                  bg=block_color, bd=0).grid(padx=0, row=0, column=3)
            Label(self.title_line, text=copyright,
                  font=text_font).grid(padx=5, row=0, column=4)

            for col, wt in ((0, 3), (2, 1), (4, 1)):
                self.title_line.columnconfigure(col, weight=wt, minsize=0)
            self.title_line.grid(row=1, column=0, sticky='ew')
            self.title_separator = \
                Frame(self.master, height=1, bg=block_color, bd=0)
            self.title_separator.grid(row=2, column=0, sticky='ew')


# The primary work area is built, consisting of the main grid, underlying
# mini-grids, and the word list panels.
# Note: the term 'grid' is overloaded.  It is both an application concept
# as well as a Tk geometry manager.

    def add_work_area(self, master, app):    # Add grids and word listboxes
        self.app_frame = Frame(master)
        grid_area = Frame(self.app_frame)
        main = self.create_grid(app, grid_area, 0,
                                main_grid_size, main_grid_show)
        main.pack(padx=0, pady=0, fill=BOTH, expand=YES)

        mini_frame = Frame(grid_area)        # Mini-grids go in alt frame
        for rc in (0,2):                     # Make mini-grids resizeable
            mini_frame.rowconfigure(rc, weight=1, minsize=0)
            mini_frame.columnconfigure(rc, weight=1, minsize=0)
        for i,r,c in ((1,0,0), (2,0,2), (3,2,0), (4,2,2)):
            self.create_grid(app, mini_frame, i, mini_grid_size) \
                .grid(row=r, column=c, padx=0, pady=0)   # grid geometry mgr
        Frame(mini_frame).grid(pady=1, row=1, column=0)
        Frame(mini_frame).grid(padx=1, row=0, column=1)
        self.mini_frame = mini_frame
        self.main_grid = main
        self.grid_area = grid_area
        mini_frame.place(
            anchor=NW, relx=0, rely=0, relwidth=1.0, relheight=1.0)
        mini_frame.lower(main)    # main grid on top initially

        boxes = self.create_wordboxes(app, self.app_frame)
        self.temp_msg_panel = self.build_temp_msg_panel(app, grid_area)
        self.search_panels = [
            self.build_search_panel(app, grid_area, dir) for dir in (0,1) ]
        Frame(self.app_frame).grid(pady=1, row=0, column=0)
        Frame(self.app_frame).grid(pady=1, row=0, column=2)

        if app_prefs['wide_layout']:
            boxes[0].grid(padx=5, pady=1, row=1, column=0, sticky='ns')
            vbar1 = Frame(self.app_frame, width=1, height=1,
                          bg=block_color, bd=0)
            vbar1.grid(padx=0, pady=0, row=0, rowspan=2, column=1, sticky='ns')
            grid_area.grid(padx=0, pady=0, row=1, column=2, sticky='news')
            vbar2 = Frame(self.app_frame, width=1, height=1,
                          bg=block_color, bd=0)
            vbar2.grid(padx=0, pady=0, row=0, rowspan=2, column=3, sticky='ns')
            boxes[1].grid(padx=5, pady=1, row=1, column=4, sticky='ns')
            self.app_frame.columnconfigure(2, weight=1, minsize=0)
            hbar1 = Frame(self.app_frame, width=1, height=1,
                          bg=block_color, bd=0)
            hbar1.grid(padx=0, pady=0, row=2, column=1, columnspan=3,
                       sticky='ew')
        else:
            grid_area.grid(padx=0, pady=0, row=1, column=0, sticky='news')
            vbar = Frame(self.app_frame)
            vbar.grid(padx=3, pady=0, row=0, rowspan=2, column=1, sticky='ns')
            boxes.grid(padx=1, pady=1, row=1, column=2, sticky='ns')
            Frame(self.app_frame).grid(padx=1, row=0, rowspan=2, column=3)
            self.app_frame.columnconfigure(0, weight=1, minsize=0)
        self.app_frame.rowconfigure(1, weight=1, minsize=0)

        # the following bindings are made to the whole application because
        # they can't be attached to the grid canvas widgets
        renum_accels = ['<Control-u>']
        if on_osx: renum_accels.insert(0, '<Command-u>')
        renum_action = EventHandler('Renumber word',
                                    lambda event: app.renumber_word_action(0,
                                                    *app.find_grid_cell()[1:]))
        for accel in renum_accels:
            wrapped_bind(master, accel, renum_action)
        whiten_accels = ['<Control-w>']
        if on_osx: whiten_accels.insert(0, '<Command-w>')
        whiten_action = EventHandler('Whiten/blacken one block',
                                     lambda event: app.place_one_block())
        for accel in whiten_accels:
            wrapped_bind(master, accel, whiten_action)

        if on_win:
            # Mouse wheel bindings need to go at top, then actions are done
            # as needed for mouse location as encoded in sess.focus_region.
            def wheel_scroll(toggle, event):
                if app.sess.focus_region < 0: return   # not grid or word panel
                if event.delta > 0: scroll = -1
                else:               scroll = 1
                # invoke handler by cursor location for word panel or grid
                self.wheel_action[app.sess.focus_region](toggle, scroll)
            wrapped_bind(master, '<MouseWheel>', lambda ev: wheel_scroll(0, ev),
                         'Mouse wheel')
            wrapped_bind(master, '<Shift-MouseWheel>',
                         lambda ev: wheel_scroll(1, ev), 'Shift mouse wheel')


    def add_popup_menu(self, app, dir):   # for right click menu
        def gen_popup_cmd(proc, args):
            def popup_cmd():
                id, row, col = app.eph.popup_args
                paint_cell_marker(self.grids[id], row, col)
                app.start_action()
                proc(*args+app.eph.popup_args)
            return EventHandler('Popup menu: %s' % proc.__name__, popup_cmd)
        def post_command():
            # save estimated cell number in case it gets reset during
            # mouse excursions while traversing menu
            app.eph.save_est_cell_nums = \
                (app.eph.est_cell_num, app.eph.est_cell_num_key)
            id, row, col = app.eph.popup_args
            paint_cell_marker(self.grids[id], row, col)
            app.eph.popup_posting = 1
        popup_menu = Menu(self.app_frame, font=menu_font,
                          postcommand=post_command)
        self.popup[dir] = popup_menu

        def renumber_action(id, row, col):
            app.eph.est_cell_num, app.eph.est_cell_num_key = \
                app.eph.save_est_cell_nums
            app.renumber_word_action(1, id, row, col)
        if on_osx: renum_accel = 'Command-U'
        else:      renum_accel = 'Ctrl+U'
        popup_menu.add_command(label='Renumber Word', accelerator=renum_accel,
                               command=gen_popup_cmd(renumber_action, ()))
        popup_menu.add_separator()

        popup_menu.add_command(label='Move %s Word' % dir_text[dir],
            command=gen_popup_cmd(app.start_single_word_trans_action, (dir,)))
        popup_menu.add_command(label='Unpaste %s Word' % dir_text[dir],
            command=gen_popup_cmd(app.del_word_grid_action, (dir,)))
        popup_menu.add_command(label='Delete %s Word' % dir_text[dir],
            command=gen_popup_cmd(app.del_word_all_action, (dir,)))
        popup_menu.add_separator()

        popup_menu.add_command(label='Move All Words on Grid',
            command=gen_popup_cmd(app.start_all_words_translation, ()))
        popup_menu.add_command(label='Move Adjacent Words',
            command=gen_popup_cmd(app.start_adjacent_words_translation, ()))
        popup_menu.add_command(label='Move Connected Words',
            command=gen_popup_cmd(app.start_connected_words_translation, ()))
        popup_menu.add_separator()

        for lab,x,y,curs in (('Upper Left',0,0,'bottom_right_corner'),
                             ('Upper Right',1,0,'bottom_left_corner'),
                             ('Lower Left',0,1,'top_right_corner'),
                             ('Lower Right',1,1,'top_left_corner')):
            popup_menu.add_command(label='Move %s Region' % lab, command=\
                 gen_popup_cmd(app.start_region_translation, (x,y,curs)))
        popup_menu.add_separator()

        popup_menu.add_command(label='Move Left Region Using Diagonal',
            command=gen_popup_cmd(app.start_diagonal_region, (0,)))
        popup_menu.add_command(label='Move Right Region Using Diagonal',
            command=gen_popup_cmd(app.start_diagonal_region, (1,)))
        popup_menu.add_separator()

        popup_menu.add_command(label='Move Selected Words Again',
            command=gen_popup_cmd(app.redo_word_translation, ()))
        popup_menu.add_separator()

        popup_menu.add_command(label='Wrap Rows around to Left',
                   command=gen_popup_cmd(app.wrap_grid_horiz, ()))
        popup_menu.add_separator()

        for text, toggle in (('Blacken', 0), ('Whiten', 2)):
            popup_menu.add_command(label='%s Square(s)' % text,
                command=gen_popup_cmd(app.place_block_menu, (toggle,)))
        if on_osx: whiten_accel = 'Command-W'
        else:      whiten_accel = 'Ctrl+W'
        popup_menu.add_command(label='Blacken/Whiten One Square',
                               accelerator=whiten_accel,
                               command=gen_popup_cmd(app.place_one_block, ()))

        def unmap_popup(event):
            for id in range(num_grids):
                self.grids[id].delete('visit')
            if app.eph.popup_posting == 1:
                id = app.eph.popup_args[0]
                self.grids[id].delete('marker')
            app.eph.popup_posting = 0
        wrapped_bind(popup_menu, '<Unmap>', unmap_popup, 'Unmap popup')
        

# ---------- Build initial GUI structures ---------- #

# The main grid and mini-grids are identical except for size.  Each has
# a large canvas plus two thin canvases for the numeric rulers, one above
# and one to the left.  They are scrolled synchronously, according to
# the direction of motion.

    def create_grid(self, app, app_fr, id, size, show=None):
        if show == None: show = size
        fr = Frame(app_fr)
        full = size * cell_size
        num_col = Canvas(fr, borderwidth=0, xscrollincrement=cell_size,
                         highlightthickness=0, selectborderwidth=0,
                         width=show*cell_size+1, height=10,
                         scrollregion=(0, 0, full+1, 10))
        num_row = Canvas(fr, borderwidth=0, yscrollincrement=cell_size,
                         highlightthickness=0, selectborderwidth=0,
                         width=11, height=show*cell_size+1,
                         scrollregion=(0, 0, 11, full+1))
        for c in range(1, size+1):
            if c % 5 == 0:
                num_col.create_text((c-1)*cell_size+half_cell_size, 5,
                                    text=str(c), font=num_font, fill='gray60')
                num_row.create_text(6, (c-1)*cell_size+half_cell_size,
                                    text=str(c), font=num_font, fill='gray60')
        canv = Canvas(fr, borderwidth=0, background=word_bg_color,
                      highlightthickness=0, selectborderwidth=0,
                      xscrollincrement=cell_size, yscrollincrement=cell_size,
                      width=show*cell_size+1, height=show*cell_size+1,
                      scrollregion=(0, 0, full+1, full+1))
        self.grids[id] = canv
        for i in list(range(1, size+1)) + [0]:  # do top/left lines last
            offset = i*cell_size
            if i%10 == 0: line_color = rule10_color
            elif i%5 == 0: line_color = rule5_color
            else:        line_color = block_color
            canv.create_line(0, offset, full, offset, fill=line_color)
            # remember last tag from initial grid lines for use in future
            # tag_lower operations
            base_tag = \
                canv.create_line(offset, 0, offset, full, fill=line_color)
        self.base_tag[id] = base_tag

        def horiz_scroll(*args):
            num_col.xview(*args)
            canv.xview(*args)
        def vert_scroll(*args):
            num_row.yview(*args)
            canv.yview(*args)
        def map_grid_posn(x, y):
            return  int(canv.canvasx(x)), int(canv.canvasy(y))
        self.map_grid_posn[id] = map_grid_posn
        def button_cmd(event_spec, proc):
            return EventHandler('Grid %d %s' % (id, event_spec),
                                lambda event: \
                                   proc(id, *map_grid_posn(event.x, event.y)))
        for event, handler in \
                (('<Button-1>', app.grid_click_1),
                 ('<ButtonRelease-1>', app.grid_click_1_up),
                 ('<Shift-Button-1>', app.grid_click_1_shift),
                 ('<Shift-ButtonRelease-1>', app.grid_click_1_up),
                 (right_button_down, app.grid_click_2),
                 (right_button_up, app.grid_click_2_up)):
            wrapped_bind(canv, event, button_cmd(event, handler))
        if on_osx:
            for event, handler in \
                (('<Control-Button-1>', app.grid_click_2),
                 ('<Control-ButtonRelease-1>', app.grid_click_2_up)):
                wrapped_bind(canv, event, button_cmd(event, handler))

        # alternative way to pop up context menu on OS X (single-button mice)
        # if the control-click feature isn't working:
        def simulate_right_click():
            location = app.find_grid_cell()
            if location:
                grid, id, row, col = location
            else:
                id, row, col = 0, 0, 0
            app.display_grid_popup(id, row, col)
        if on_osx:
            wrapped_bind(app.master, '<Control-m>',
                         lambda event: simulate_right_click(),
                         'Grid %d %s' % (id, '<Control-m>'))

        def motion_action(event):
            ex, ey = event.x, event.y
            app.move_quiescent_xy(id, ex, ey, *map_grid_posn(ex, ey))
        self.grid_motion_action[id] = \
            EventHandler('Grid %d motion' % id, motion_action)
        wrapped_bind(canv, '<Motion>', self.grid_motion_action[id])

        self.indicators[id] = [None, None] # triangle object for each direction
        def destroy_indicators():
            for num_widget in self.indicators[id]:
                if num_widget:    # remove indicator widgets if present
                    num_widget.delete('indic')
                    num_widget.delete('bar')
            self.indicators[id] = [None, None]
        self.destroy_indicators[id] = destroy_indicators

        def create_indicators(dir=None, init_posn=None):
            # dir = 0,1 for one dir; 2 for both
            # corners = (ul_row, ul_col, lr_row, lr_col) for region
            destroy_indicators()          # in case old one still exists
            if dir == None:
                dir = 1 - app.sess.next_focus
            if init_posn:
                row, col = init_posn
            else:
                px, py = app.master.winfo_pointerxy()
                x, y = map_grid_posn(px - canv.winfo_rootx(),
                                     py - canv.winfo_rooty())
                row, col = y // cell_size, x // cell_size

            # create an indicator triangle above or to left of grid
            if dir > 0:
                midpt = col*cell_size + half_cell_size
                triangle = \
                    num_col.create_polygon(midpt-5, 2, midpt+5, 2, midpt, 10,
                                           outline='', fill=highlight_color,
                                           tags=('indic',))
                self.indicators[id][1] = num_col
            if dir != 1:
                midpt = row*cell_size + half_cell_size
                triangle = \
                    num_row.create_polygon(2, midpt-5, 2, midpt+5, 10, midpt,
                                           outline='', fill=highlight_color,
                                           tags=('indic',))
                self.indicators[id][0] = num_row

            corners = app.eph.init_corners
            if dir == 2 and corners:
                # draw bars for horiz, vert ranges of region
                top, left, bottom, right = \
                    [ (r + c) * cell_size
                      for r,c in zip((row,col,row,col), corners) ]
                num_col.create_rectangle(left, 0, right, 2, outline='',
                                         fill=highlight_color, tags=('bar',))
                num_row.create_rectangle(0, top, 2, bottom, outline='',
                                         fill=highlight_color, tags=('bar',))
        self.create_indicators[id] = create_indicators

        def enter_canvas():
            if app.sess.focus_region == 2 + id:
                return       # already entered this grid
            app.sess.focus_region = 2 + id
            if app.perm.final: return
            dir = 1 - app.sess.next_focus
#            self.word_ent[dir].focus_set()
            canv.after_cancel(app.eph.visit_id)
            if not app.eph.multistep_mode:
                if app.sess.key_navigation:
                    app.set_key_cursor(app.temp.key_cursors[id][1:3])
                else:
                    app.adjust_word_number(dir, 0, delay_factor=1)
        wrapped_bind(fr, '<Enter>', lambda *args: enter_canvas(),
                     'Grid %d enter' % id)
        self.enter_grid[id] = enter_canvas
                                          
        def exit_canvas():
            if app.sess.focus_region != 2 + id:
                return       # already exited this grid
            canv.after_cancel(app.eph.scroll_id)
            canv.after_cancel(app.eph.visit_id)
            destroy_indicators()
            if app.sess.key_navigation and not app.perm.final:
                gr, gc = app.temp.key_cursors[id][1:3]
                paint_key_cursor(canv, 2, gr, gc, 'letter')
            # offset prev posn so it will be recognized that cursor went
            # off the canvas but the value can still be recovered
            app.eph.prev_posn = [ p - 1000 for p in app.eph.prev_posn ]
            if not app.eph.popup_posting:
                for tag in ('infer', 'infer2', 'visit'):
                    canv.delete(tag)
                app.clear_listbox_indicator(1 - app.sess.next_focus)
                app.sess.focus_region = -1
        wrapped_bind(fr, '<Leave>', lambda *args: exit_canvas(),
                     'Grid %d leave' % id)
        self.leave_grid[id] = exit_canvas
                                          

        hscroll = FlatScrollbar(fr, command=horiz_scroll, width=14,
                                orient=HORIZONTAL)
        vscroll = FlatScrollbar(fr, command=vert_scroll, width=14)
        num_col.configure(xscrollcommand=hscroll.set)
        canv.configure(xscrollcommand=hscroll.set)
        canv.configure(yscrollcommand=vscroll.set)

        fr.rowconfigure(0, weight=0, minsize=0)
        fr.rowconfigure(1, weight=1, minsize=0)
        fr.columnconfigure(0, weight=0, minsize=0)
        fr.columnconfigure(1, weight=1, minsize=0)

        num_col.grid(padx=1, row=0, column=1, sticky='ew')
        num_row.grid(padx=2, pady=1, row=1, column=0, sticky='ns')
        canv.grid(padx=1, pady=1, row=1, column=1, sticky='news')
        vscroll.grid(padx=1, pady=1, row=1, column=2, sticky='ns')
        hscroll.grid(padx=1, pady=1, row=2, column=1, sticky='ew')
        size_float = float(size)

        def scroll_grid(row, col):         # used in error handlers
            canv.delete('infer')
            canv.delete('infer2')
            canv.delete('visit')
            canv.xview_moveto(col/size_float)
            canv.yview_moveto(row/size_float)
            num_col.xview_moveto(col/size_float)
            num_row.yview_moveto(row/size_float)
        self.scroll_grid[id] = scroll_grid

        def delta_wheel_scroll(toggle, delta):      # Mouse wheel handler
            if toggle: dir = app.sess.next_focus
            else:      dir = 1 - app.sess.next_focus
            if dir:    vert_scroll('scroll', delta, UNITS)
            else:      horiz_scroll('scroll', delta, UNITS)
        if on_win:
            # register wheel scroller for event handlers in word panels
            self.wheel_action[id+2] = delta_wheel_scroll
        elif on_osx:
            def wheel_scroll(toggle, event):
                if event.delta > 0: scroll = -1
                else:               scroll = 1
                delta_wheel_scroll(toggle, scroll)
            wrapped_bind(canv, '<MouseWheel>', lambda ev: wheel_scroll(0, ev),
                         'Mouse wheel')
            wrapped_bind(canv, '<Shift-MouseWheel>',
                         lambda ev: wheel_scroll(1, ev), 'Shift mouse wheel')
        else:
            wrapped_bind(canv, '<Button-4>',
                         lambda e: delta_wheel_scroll(0, -1), 'Delta wheel')
            wrapped_bind(canv, '<Button-5>',
                         lambda e: delta_wheel_scroll(0, 1), 'Delta wheel')
            wrapped_bind(canv, '<Shift-Button-4>',
                         lambda e: delta_wheel_scroll(1, -1), 'Delta wheel')
            wrapped_bind(canv, '<Shift-Button-5>',
                         lambda e: delta_wheel_scroll(1, 1), 'Delta wheel')
        return fr

# Stacking order for canvas tags:

# aids           -- lines for multistep commands
# m_aids         -- cell border for drag clashes
# marker         -- temp objects for multistep commands
# infer, infer2  -- inferred numbers
# preview        -- letters, background during preview, dragging
# visit          -- temp word display
# letter, block  -- for words, permanent blocks
# key_cursor     -- for key navigation mode
# symm           -- symmetric blocks
# outer          -- don't clear, session setting

# Following are drawn on top but don't interfere with normal display.

# indic   -- grid indicator triangles
# bar     -- grid indicator bars
# error   -- error message objects
# final   -- finalization objects; also view-grid feature
# test    -- test only

# Unconfirmed warnings and other notifications pop up a small, temporary
# window at the bottom of the main gird area to display a message.

    def build_temp_msg_panel(self, app, parent):
        temp_msg = ColoredFrame(parent, bd=4, color=rule5_color)
        msg = Message(temp_msg, text='', aspect=1200, foreground=custom_red,
                      relief=FLAT, bg=message_bg, padx=20, pady=10)
        msg.pack()
        def hide_msg_panel():
            temp_msg.place_forget()
        def show_msg_panel():
            temp_msg.place(anchor=S, relx=0.5, rely=1.0)
        return msg, show_msg_panel, hide_msg_panel


# ---------- Word panel listboxes ---------- #

# The wordbox panel stacks Across and Down subpanels, with buttons in between.
# This is the original short format.  Now there is also an long format for the
# wide-layout user option.

    def create_wordboxes(self, app, app_fr):
        # save widgets when built for later reference, indexed by direction:
        self.panel_head   = [0,1]       # Across, Down headers
        self.next_num     = [0,1]
        self.word_count   = [0,1]
        self.word_ent     = [0,1]
        self.enter_button = [0,1]
        self.wordbox      = [0,1]
        self.toggle_focus_proc = [0,1]
        self.pattern_ent  = [0,1]       # for search panels
        self.searchbox    = [0,1]       #
        if app_prefs['wide_layout']:
            return self.create_wordboxes_long(app, app_fr)
        else:
            return self.create_wordboxes_short(app, app_fr)
        
    def create_wordboxes_short(self, app, app_fr):
        fr = Frame(app_fr)
        a_fr = self.build_word_box(app, fr, 0, dir_text[0],
                                   *app.word_event_handlers(0))
        a_fr.grid(row=0, column=0, sticky='nsew')  # 'ns')
        fr.rowconfigure(0, weight=1, minsize=0)
        but_fr = Frame(fr)
        Frame(but_fr).pack(pady=2)
        MediumButton(but_fr, text='Undo',
                   command=EventHandler('Undo button', lambda : app.undo())
                   ).pack(side=LEFT, padx=5)
        MediumButton(but_fr, text='Swap Grids',
                   command=EventHandler('Swap grids button',
                                        lambda : app.swap_grids())
                   ).pack(side=RIGHT, padx=5)
        but_fr.grid(row=1, column=0, pady=5)
        d_fr = self.build_word_box(app, fr, 1, dir_text[1],
                                   *app.word_event_handlers(1))
        d_fr.grid(row=2, column=0, sticky='nsew')
        fr.rowconfigure(2, weight=1, minsize=0)
        self.box_frames = [a_fr, d_fr]   # for kbd shortcut to swap focus
        return fr
        
    def create_wordboxes_long(self, app, app_fr):
        a_fr = self.build_word_box(app, app_fr, 0, dir_text[0],
                                   *app.word_event_handlers(0))
        d_fr = self.build_word_box(app, app_fr, 1, dir_text[1],
                                   *app.word_event_handlers(1))
        self.box_frames = [a_fr, d_fr]   # for kbd shortcut to swap focus
        return a_fr, d_fr

# For each direction (0 = Across, 1 = Down), create an entry, a row of buttons,
# and a listbox to store words.

    def build_word_box(self, app, parent, dir, direc, *procs):
        enter_proc, delete_proc, select_proc = procs    # already wrapped
        fr = Frame(parent, relief=FLAT)
        label_fr = Frame(fr)
        next_num = Label(label_fr, text='', width=6, anchor=W,
                         foreground=highlight_color, font=text_font)
        next_num.pack(padx=5, pady=0, side=LEFT)
        word_count = Label(label_fr, text='0 / 0', width=6, anchor=E,
                           font=text_font)
        word_count.pack(padx=5, pady=0, side=RIGHT)
        self.panel_head[dir] = Label(label_fr, text=direc, font=heading1_font)
        self.panel_head[dir].pack(pady=0, fill=X, expand=YES, side=LEFT)
        label_fr.pack(padx=5, pady=0, fill=X)
        self.next_num[dir]   = next_num
        self.word_count[dir] = word_count

        if on_win:   entry_font = text_font
        elif on_osx: entry_font = text_font
        else:        entry_font = text_font
        ent_fr = Frame(fr)
        word_ent = entry_widget(ent_fr, width=20)
        word_ent.pack(side=LEFT, padx=3, fill=X, expand=YES)
        entry_text = app.sess.word_entry_text

        # Keyboard events are checked for special cases that need treatment,
        # such as +/- keys and digits.  These checks need to execute after
        # the built-in key bindings for the Entry widget so any numbers
        # typed by the user can be processed.

        def special_key_checks(event):
            match = modifier_keysym_pattern.search(event.keysym)
            if match:
                group = match.group(1)
                if group == 'Shift':
                    app.close_temp_displays()    # remove warnings, temp words
                    return
                if group in ('Control', 'Meta', 'Alt', 'Super') :
                    # skip modifiers to avoid early/extra adjustments/resets
                    return
            if event.keysym == 'Escape': return
            new_text = word_ent.get().strip()
            have_digits_now = len(num_prefix.split(new_text)) == 2
            if event.keysym in num_adj_up_keysyms:
                app.adjust_word_number(dir, 1)
            elif event.keysym in num_adj_down_keysyms:
                app.adjust_word_number(dir, -1)
            elif have_digits_now:
                had_digits_before = len(num_prefix.split(entry_text[dir])) == 2
                if not had_digits_before:
                    # clear infer/next num displays =>
                    #   user is starting to type a word number
                    for canv in app.gui.grids:
                        # later pick only one grid?
                        for tag in ('infer', 'infer2', 'visit'):
                            canv.delete(tag)
                    next_num.config(text='')
                new_num, rest = parse_number(new_text)
                if new_num > 0:
                    app.set_listbox_indicator(dir, new_num,
                                              app.wordbox_index(dir, new_num))
                else:
                    app.set_listbox_indicator(dir, None)
                app.adjust_word_number(dir, 0)
                app.adjust_temp_word_display(dir, new_text)
            else:
                # repaint entry/grid numbers in case they're gone or changed
                app.adjust_word_number(dir, 0)
                # repaint temporary word display on grid
                app.adjust_temp_word_display(dir, new_text)
            entry_text[dir] = new_text

        special_key_hdlr = EventHandler('Entry keypress', special_key_checks)

        def special_key_handler(event):
            # delay handling so digit chars can be placed in Entry widget
            word_ent.after(10, special_key_hdlr, event)
            if event.keysym in undisplayed_keysyms:
                # suppress display of keysyms being used as commands
                return 'break'
        wrapped_bind(word_ent, '<Key>', special_key_handler, 'Special key')

        for event, args in (
            ('<Up>', (1, 1, -1,)), ('<Down>', (1, 1, 1,)),
            ('<Left>', (0, 1, -1, 1)), ('<Right>', (0, 1, 1, 1)),
            ('<Shift-Up>', (1, 0, -1,)), ('<Shift-Down>', (1, 0, 1,)),
            ('<Shift-Left>', (0, 0, -1, 1)), ('<Shift-Right>', (0, 0, 1, 1)),
            ('<Tab>', (2, 0, 4, 1)), ('<<ReverseTab>>', (2, 0, -4, 1)),
            ):
            wrapped_bind(word_ent, event,
                         lambda ev,args=args:
                             app.move_key_cursor_event(*args),
                         'Grid cursor command')
        self.word_ent[dir] = word_ent
        def clear_word_ent():
            word_ent.delete(0, END)
            entry_text[dir] = ''
            app.temp.sel_num_word[dir] = None
            prev_num = app.temp.next_word_num[dir]
            next_num.config(text=str(prev_num))
            app.set_listbox_indicator(dir, prev_num,
                                      app.wordbox_index(dir, prev_num),
                                      see_index=1)
            self.wordbox[dir].selection_clear(0, END)
            word_ent.focus_set()   # ensure focus is maintained

        c_fr = FixedFrame(ent_fr)
        Button(c_fr, text='C',
               command=EventHandler('Clear entry %s' % direc,
                                    clear_word_ent)).pack()
        c_fr.pack(side=LEFT, padx=1)
        ent_fr.pack(padx=10, pady=0, fill=X)

        button_fr = Frame(fr)
        for text, default, cmd in \
            (('Enter',  1, enter_proc),
             ('Delete', 0, delete_proc),
             ('Find',   0, EventHandler('Find %s' % direc,
                                        lambda : app.search_for_word(dir)))):
            if using_ttk or using_tile:
                button = Button(button_fr, text=text, width=8, command=cmd)
                button.pack(side=LEFT, padx=5)
            else:
                button = ThinButton(button_fr, text=text, command=cmd,
                                    min_width=6)
                button.pack(side=LEFT, padx=5)
            if default:
                self.enter_button[dir] = default_button = button
                wrapped_bind(word_ent, '<Return>', cmd)
        button_fr.pack(padx=0, pady=5)
        if on_win:   wordbox_font = text_font
        elif on_osx: wordbox_font = font_var(-1)
        else:        wordbox_font = small_text
        wordbox = word_list_multi(fr, wordbox_height, select_proc, padx=2,
                                  font=wordbox_font)
        self.wordbox[dir] = wordbox

        def pop_up_alt_words(event):
            index = wordbox.nearest(event.y)
            if index < 0: return               # emtpy listbox
            if app.temp.puz_defn:
                num = app.temp.puz_defn.nums[dir][index]
            else:
                num = app.perm.nums[dir][index]  # exists if listbox entry does
            alts = app.perm.alt_words[dir].get(num, [])
            popup = Menu(self.app_frame, font=menu_font)
            popup.add_command(label=' Alternative answers', font=italic_font)
            popup.add_command(label='   for %d %s' % (num, dir_text[dir]),
                              font=italic_font)
            popup.add_separator()

            for word in alts:
                cmd = EventHandler('Alt word',
                                   lambda d=dir, n=num, w=word:
                                       app.swap_alt_word(d, n, w))
                label = '  %s  (%d) ' % (word, len(word))
                popup.add_command(label=label, command=cmd)
            if not alts:
                popup.add_command(label='  --- None ---', state=DISABLED)
            popup.tk_popup(event.x_root, event.y_root)

        wrapped_bind(wordbox, right_button_down, pop_up_alt_words, 'Pop up')
        if on_osx:
            wrapped_bind(wordbox, '<Control-Button-1>',
                         pop_up_alt_words, 'Pop up')

        # when mouse cursor enters a word list frame, clear opposite word
        # entry and restore previous word entry for this direction
        def toggle_focus():
            if root.tk.call('wm', 'stackorder', '.')[-1] != '.':
                return     # toggle only when main window is on top
            # entry_text should always have latest user-typed characters
            word_ent.delete(0, END)
            word_ent.insert(END, entry_text[dir])
            word_ent.focus_set()
            if app.perm.final:
                app.set_grid_cursors(2)
            else:
                if not app.eph.multistep_mode:
                    app.set_grid_cursors(dir)
                self.status_line['text'] = \
                    'Now entering %s words.' % dir_text[dir]
            self.word_ent[1-dir].delete(0, END)
            app.sess.next_focus = 1-dir   # used by keyboard accelerator
        self.toggle_focus_proc[dir] = toggle_focus

        # For most GUI platforms we indicate default buttons.
        # Motif-style active buttons are too large here, so for other
        # GUI platforms we set text color to blue for defaults.
        # Return key bindings are provided in any case.
        if using_ttk or using_tile or on_win or on_aqua:
            def activate_default_button(*args):
                default_button['default'] = ACTIVE
            def deactivate_default_button(*args):
                default_button['default'] = NORMAL
        else:
            def activate_default_button(*args):
                default_button['fg'] = default_fg
            def deactivate_default_button(*args):
                default_button['fg'] = 'black'
        wrapped_bind(fr, '<FocusIn>', activate_default_button, 'Focus in')
        wrapped_bind(fr, '<FocusOut>', deactivate_default_button, 'Focus out')

        def enter_frame (event):
            if app.sess.next_focus == dir:
                toggle_focus()
            app.sess.focus_region = dir
            if not app.perm.final and \
                    (app.eph.est_cell_num_key + app.eph.est_cell_num == 0
                     or len(num_prefix.split(word_ent.get())) < 2):
                # regenerate num, indicator unless number already present
                app.adjust_word_number(dir, 0, see_index=1, delay_factor=1)
        wrapped_bind(fr, '<Enter>', enter_frame, 'Enter word frame')

        def leave_frame (event):
            next_num.config(text='')
            app.clear_listbox_indicator(dir)
            app.sess.focus_region = -1
        wrapped_bind(fr, '<Leave>', leave_frame, 'Leave word frame')
        # Mouse wheel handler for Windows only. Wheel events for Linux give
        # Button-4/5 events. Invoke grid scrolling when cursor is over grids.
        if on_win:
            def delta_wheel_scroll(toggle, delta):
                wordbox.yview_scroll(delta, PAGES)
            self.wheel_action[dir] = delta_wheel_scroll
        return fr


# ---------- Word search panels ---------- #

# Word search pops up a small window, then collects a word list from
# current word items (with acquired letters) in the listbox.

    def build_search_panel(self, app, parent, dir):
        direc = dir_text[dir]
        fr = ColoredFrame(parent, bd=4, color=highlight_color)
        def hide_search_panel():
            deactivate_default_button()
            fr.place_forget()
            self.word_ent[1 - app.sess.next_focus].focus_set()
        inner_fr = Frame(fr)
        Label(inner_fr, text='Searching %s' % direc,
              font=bold_font).pack(pady=2)
        ent_fr = Frame(inner_fr)
        pattern_ent = entry_widget(ent_fr, width=20)
        pattern_ent.pack(side=LEFT, padx=3, fill=X, expand=YES)
        pattern_ent_id = \
            pattern_ent.winfo_parent() + '.' + pattern_ent.winfo_name()
        pattern_ent.bindtags(('Entry', pattern_ent_id, '.', 'all'))
        self.pattern_ent[dir] = pattern_ent
        def clear_pattern_ent():
            pattern_ent.delete(0, END)
            wordbox.delete(0, END)
        c_fr = FixedFrame(ent_fr)
        Button(c_fr, text='C', 
               command=EventHandler('Clear search entry %s' % direc,
                                    clear_pattern_ent)).pack()
        c_fr.pack(side=LEFT, padx=1)
        ent_fr.pack(padx=2, pady=3, fill=X)
        def select_proc(word_entry):
            # on item selection, place it in word entry for user action
            index = wordbox.nearest(word_entry.y)
            num,word = string.split(wordbox.get(index))
            self.word_ent[dir].delete(0, END)
            self.word_ent[dir].insert(0, '%s %s' % (num,word))
            app.temp.sel_num_word[dir] = (int(num), word, None)
            # hide window but wait until button-up event
        wordbox = word_list(inner_fr, 6,
                            EventHandler('Search %s selection' % direc,
                                         select_proc),
                            padx=5)
        wrapped_bind(wordbox, '<ButtonRelease-1>',
                     lambda event: hide_search_panel(), 'Hide search panel')
        self.searchbox[dir] = wordbox

        # search patterns support limited regular expressions:
        valid_pattern = re.compile('[a-zA-Z.*?]*\Z')
        def update_search(event):
            wordlist = [ (item[0],
                          item[1].split(clue_separator)[0] \
                              .split()[1].split(',')[0])
                         for item in self.wordbox[dir].get(0, END) ]
            wordbox.delete(0, END)
            pattern = pattern_ent.get().strip()
            if not valid_pattern.match(pattern):
                user_dialog(showerror, *error_messages['invalid_pattern'])
                return
            if pattern:
                pattern = re.sub('\?', '\\?', pattern)  # protect placeholders
                pattern = re.compile(re.sub('\*', '.*', pattern))
                for nw in wordlist:
                    if pattern.search(nw[1]):
                        wordbox.insert(END, '%s %s' % nw)
            set_scrollbars_top(wordbox)
        def start_search(event, location):
            if location:
                init_pattern = app.infer_search_pattern(dir, *location)
            else:
                init_pattern = pattern_ent.get()
            pattern_ent.delete(0, END)
            pattern_ent.insert(END, init_pattern)
            # ensure pattern is inserted in entry widget before searching
            app.master.update_idletasks()
            update_search(None)
        corners = (NW,NE), (SW,SE)
        def slide_search(x):
            fr.place(anchor=corners[dir][x], relx=x, rely=dir)

        bottom_buttons = Frame(inner_fr)
        for face, event, default, proc in \
            (('<', 'Slide search left', 0, lambda : slide_search(0)),
             ('Rescan', 'Restart search', 0,
              lambda : start_search(None, None)),
             ('Hide', 'Hide search panel', 1,
              lambda *args: hide_search_panel()),
             ('>', 'Slide search right', 0, lambda : slide_search(1))):
            if using_ttk or using_tile:
                button = ThinButton(bottom_buttons, text=face,
                                    min_width=2+len(face),
                                    command=EventHandler(
                                              '%s %s' % (event, direc), proc))
                button.pack(side=LEFT, padx=4)
            else:
                button = ThinButton(bottom_buttons, text=face, min_width=1,
                                    command=EventHandler(
                                              '%s %s' % (event, direc), proc))
                button.pack(side=LEFT, padx=2)
            if default:
                default_button = button
                wrapped_bind(pattern_ent, '<Return>', proc, 'Search')
        bottom_buttons.pack(padx=5, pady=5)
        inner_fr.pack()
        
        # following binding needs to follow button creation above so
        # default Return binding is acted on first
        wrapped_bind(pattern_ent, '<Key>', update_search,
                     'Search keypress %s' % direc)
        # For most GUI platforms we indicate default buttons.
        # Motif-style active buttons are too large here, so for other
        # GUI platforms we set text color to blue for defaults.
        # Return key bindings are provided in any case.
        if using_ttk or using_tile or on_win or on_aqua:
            def activate_default_button(*args):
                default_button['default'] = ACTIVE
            def deactivate_default_button(*args):
                default_button['default'] = NORMAL
                if on_aqua: app.master.update()   # prevent lingering buttons
        else:
            def activate_default_button(*args):
                default_button['fg'] = default_fg
            def deactivate_default_button(*args):
                default_button['fg'] = 'black'
        wrapped_bind(fr, '<FocusIn>', activate_default_button, 'Focus in')
        wrapped_bind(fr, '<FocusOut>', deactivate_default_button, 'Focus out')
        def enter_search_panel():
            if root.tk.call('wm', 'stackorder', '.')[-1] == '.':
                # set focus only when main window is on top
                pattern_ent.focus_set()
        def leave_search_panel():
            if root.tk.call('wm', 'stackorder', '.')[-1] == '.':
                # set focus only when main window is on top
                self.word_ent[1 - app.sess.next_focus].focus_set()
        wrapped_bind(fr, '<Enter>', lambda event: enter_search_panel(),
                     'Enter search frame %s' % direc)
        wrapped_bind(fr, '<Leave>', lambda event: leave_search_panel(),
                     'Leave search frame %s' % direc)
        ### Mouse wheel handler (Windows only; Linux works without)
        if on_win:
            def wheel_scroll(event):
                if event.delta > 0: scroll = -1
                else:               scroll = 1
                wordbox.yview_scroll(scroll, PAGES)
            wrapped_bind(pattern_ent, '<MouseWheel>', wheel_scroll,
                         'Search wheel scroll')
        return (fr, start_search, slide_search)
            

# ----- End of class GUI_elements ----- #


# ---------- Main application data class ---------- #

class DiagData(object):
    def __init__(self, master):
        make_app_menubar(master, self.app_menus(),
                         ('Preferences...',
                          self.change_preferences, 0),
                         ('About Diagnil', self.about, 0), 1)
        self.master = master
        self.sess   = SessionState(self)
        self.eph    = EphemeralState()
        self.gui    = GUI_elements(master, self)

        self.new_clueless(check=0, clear=0,
                          initialized=0)       # initializes perm, aux, temp
        self.new_puzzle_file()

        if self.sess.key_navigation:           # display initial key cursors
            for canv in self.gui.grids:
                paint_key_cursor(canv, 2, 0, 0, 'letter')

        # Set initial keyboard focus (in Across panel)
        self.master.update_idletasks()
        self.toggle_entry_focus()

        # Need to create following word wrapper classes after building
        # the GUI so widget sizes are set first.  They might sleep for
        # a while to wait for winfo_width to appear.
        for mlist in self.gui.wordbox:
            mlist.set_multilistbox_wrappers()


# Create menu choices for recently opened files.

    def make_recent_list(self):
        file_list = [ f for f in app_recent['open_files']
                      if os.path.exists(f) ]
        mod_times = map(mod_time_ago, map(os.path.getmtime, file_list))
        names = [ os.path.splitext(os.path.basename(f))[0] for f in file_list ]
        labels = [ '%s  --  saved %s    ' % (f, t)
                   for f, t in zip(names, mod_times) ]
        choices = [ (label, lambda f=f: self.open_puz(f), None)
                    for label, f in zip(labels, file_list) ]
        return choices

    def initial_recent_list(self):
        def open_newest():
            recent = app_recent['open_files']
            self.open_puz(recent and recent[0] or '')

        choices = self.make_recent_list()
        if len(choices) < num_recent:
            choices.extend([ (' --     ', null_proc, None) ] *
                           (num_recent - len(choices)))
        # Following must use function open_newest so Ctrl-I binding
        # can always fetch the latest file.  Later calls to
        # make_recent_list will inject file-specific commands.
        choices[0] = (choices[0][0], open_newest, None, 'i',)
        return choices

# When posting the file menu, need to refresh the Recent file values.

    def update_postcommand(self):
        update_submenu(self.master.menubar_items,
                       self.master.menu_tags['Open Recent'],
                       self.make_recent_list())

# Define main application menubar.

    def app_menus(self):
        return [['File', 0,
                 ('New', self.new_clueless, 0, 'n'),
                 ('Open',
                  [('Puzzle Folder...',
                    lambda : self.open_puz(alt_dir=self.sess.puzzle_dir),
                    0, 'o'),
                   ('Last Folder...',
                    lambda : self.open_puz(alt_dir='latest_puzzle_dir'), 0),
                   ('Other Folder...',
                    lambda : self.open_puz(alt_dir=home_directory), 0),], 0),
                 ('Open Recent', self.initial_recent_list(),
                  (5, self.update_postcommand)),
                 ('Save', self.save, 0, 's'),
                 ('Save As...',
                  [('Puzzle Folder...',
                    lambda : self.save_as(alt_dir=self.sess.puzzle_dir), 0),
                   ('Last Folder...',
                    lambda : self.save_as(alt_dir='latest_puzzle_dir'), 0),
                   ('Other Folder...',
                    lambda : self.save_as(alt_dir=home_directory), 0),], 1),
                 None,
                 ('Import Clues',
                  [('From File...', self.import_clues, 5),
                   ('From Clipboard...', lambda : self.import_clues(0), 5)],
                  0), None,
                 ('Properties...', self.show_file_properties, 0), None,
#                 ('Download Selection', self.download_selection, 0, 'd'),
#                 ('Download File...', self.download_puz, 2), None,
                 ('Delete Puzzles...', self.delete, 0, ), None,
                 ('Exit  ', self.exit, 0, 'q') ],
                ['Edit', 0,
                 ('Undo   ', self.undo, 0, 'z'),
                 ('Redo   ', self.redo, 0, 'y'),
                 ('Abort Multistep Action',
                  self.abort_multistep, 0, ('Escape', 'Esc')), None,
                 ('Recall Last Entry', self.recall_last, 7, 'l'),
                 ('Rotate Word', self.rotate_word, 0, 'r'),
                 ('Find Word...', self.search_for_word, 0, 'j'), None,
                 ('Finalize Puzzle', self.finalize_puzzle, 6), None,
                 ('Edit Imported Clues', self.edit_imported_clues, 0), None,
                 ('Session Settings...', self.change_session_settings, 0), ],
                ['View', 0,
                 ('Swap Grid Displays', self.swap_grids, 5, 'g'),
                 ('Toggle Word Entry Direction',
                  self.toggle_entry_focus, 0, 'p'), None,
                 ('Clues in Separate Window', 
                  [('All Clues', self.show_clues_window, 0),
                   ('Selected Clue(s)', self.show_selected_clues, 0) ],
                  0),
                 ('Puzzle Notes/Hints', self.show_puzzle_notes, 7),
                 ('Grid Pattern', self.view_grid_pattern, 5), None,
                 ('Set Size and Symmetry',
                  [('Current Puzzle...', self.declare_puzzle_size, 0),
                   ('Current Session...',
                    lambda : self.declare_puzzle_size(1),
                    0),
                   ('Both Puzzle and Session...',
                    lambda : self.declare_puzzle_size(2),
                    0)],
                  0), None,
                 ('Undo/Redo List', self.show_undo_redo_list, 0),
                 ('Recent Messages', self.show_message_list, 0) ],
                ['Solution', 0,
                 ('First Square Hint', self.first_square_hint, 0), None,
                 ('Check Word', self.check_soln_word, 0),
                 ('Check Position', self.check_soln_posn, 0),
                 ('Check Full Solution', self.check_solution, 0), None,
                 ('Reveal Word', self.reveal_soln_word, 0),
                 ('Reveal Position', self.reveal_soln_posn, 0),
                 ('Reveal Full Solution', self.reveal_solution, 0), None,
                 ('Unlock Solution...', self.unlock_solution, 0) ],
                ['Help', 0,
                 ("User's Guide", self.help, 0),
                 ("Quick Start", self.quick_start, 0),
                 ('Sample Grids...', self.view_samples, 0),
                 ("Diagramless Primer", self.diagramless_primer, 0) ]]


    clueful_menu_items = ('Clues in Separate Window', 'Puzzle Notes/Hints',
                          'First Square Hint')

    semi_clueful_menu_items = \
        ('Clues in Separate Window', 'Puzzle Notes/Hints',
         'Edit Imported Clues')

    solution_menu_items = \
        ('Check Word', 'Check Position', 'Check Full Solution',
         'Reveal Word', 'Reveal Position', 'Reveal Full Solution')

    dynamic_menu_items = clueful_menu_items + semi_clueful_menu_items + \
                         solution_menu_items + ('Unlock Solution...',)
