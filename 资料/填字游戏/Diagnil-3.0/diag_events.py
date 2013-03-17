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
from diag_classes   import PermState


# ---------- Class definitions ---------- #

class DiagEvents(object):
    def __init__(self, master=None): pass


# ---------- Event handling ---------- #

# We take a snapshot of the permanent puzzle state at the start of a new
# action in case we need to roll back after an error.  If the action is
# successful, this snapshot becomes the new undo state.

    def start_action(self, override_final=0):
        if self.perm.final and not override_final:
            user_dialog(showerror, *error_messages['already_final'])
            raise FalseStart
        if isinstance(self.perm, PermState):
            self.temp.recovery_state = copy.deepcopy(self.perm)
        else:
            # this case shouldn't happen -- it means perm was corrupted;
            # try to recover silently but things will break elsewhere
            trace = StringIO()
            print_exc(100, trace)
            debug_log("\n***** Invalid Perm object: *****\n\n%s\n\n%s\n"
                      % (self.perm, trace.getvalue()))
            self.perm = PermState()
        self.temp.recovery_nonperm = self.nonperm_recovery_state()
        self.eph.wordbox_posns = [ b.nearest(0) for b in self.gui.wordbox ]
        self.eph.followup_actions = []
        self.eph.action_done = 0    # indicate an action is in progress

# Handlers need to call one of the following when completing an action:
#   finish_action -- normal case, perm state changed
#   restore_state -- error case,  perm state changed
#   close_action  -- normal or error, perm state unchanged

    def finish_action(self, dir, id, key_move_aligned=0):
        # dir = None to suppress entry clearing; id = grid to clean up
        self.perform_followup_actions()
        self.temp.undo_state.append((self.temp.recovery_state,
                                     self.temp.recovery_nonperm,
                                     self.eph.action_string))
        if len(self.temp.undo_state) > app_prefs['max_undo']:
            del self.temp.undo_state[0]
        self.temp.redo_state = []
        if dir != None:
            self.sess.word_entry_text[dir] = ''
            self.gui.word_ent[dir].delete(0, END)
            self.temp.sel_num_word[dir] = None
        if dir != None and self.sess.focus_region == dir:
            self.gui.next_num[dir].config(
                text=str(self.temp.next_word_num[dir]))
#        self.temp.multiword_selection = None  # overridden by move cmds
        self.gui.puzzle_size['text'] = self.current_puzzle_size()
        if self.temp.size_symm[1]:              # apply_symmetry flag
            self.add_symmetric_blocks()
        self.emit_warnings()
        if id != None and self.sess.key_navigation:
            krow, kcol = self.temp.key_cursors[id][1:3]
            kdir = 1 - self.sess.next_focus
            if self.aux.cells[id][krow][kcol][2]:
                # key cursor now clashes with a block; advance cursor
                move_dir = kdir if key_move_aligned else 0
                self.move_key_cursor(id, kdir, move_dir, 1)
        self.check_if_done()
        self.update_word_counts()
        eval_assertion(self.state_invariant, 'Post-action check')
        self.close_action(id)
        self.refresh_save_time_status()

    def check_if_done(self):
        if self.temp.puz_defn and app_prefs['auto_complete'] and \
                not self.temp.revealed:
            cells = self.aux.cells[0]
            letter_count = 0
            for row in range(self.temp.puz_defn.height):
                for col in range(self.temp.puz_defn.width):
                    cell = cells[row][col]
                    if cell[0] or cell[1]:
                        letter_count += 1
            if letter_count != self.temp.soln_letter_count:
                return
            if self.check_cell_letters():
                try:
                    self.finalize_puzzle()
                    self.temp.undo_state.append((copy.deepcopy(self.perm),
                                                 self.temp.recovery_nonperm,
                                                 'Finalize Puzzle'))
                    if len(self.temp.undo_state) > app_prefs['max_undo']:
                        del self.temp.undo_state[0]
                    self.temp.redo_state = []
                except FalseStart:
                    pass

    def restore_state_partial(self):
        self.install_perm(self.temp.recovery_state, 0)

    def restore_state(self, id):       # id = None if no grid
        self.restore_state_partial()
        # recovery rewinds listboxes to top; need to restore positions
        for dir in (0,1): 
            self.gui.wordbox[dir].yview_scroll(self.eph.wordbox_posns[dir],
                                               UNITS)
        self.update_word_counts()
#        self.emit_warnings()       # need any warnings after errors?
        self.close_action(id)

    def close_action_partial(self, *ids):
        for id in ids:    ### consider cleanup of all grids as default
            if id == None: continue
            grid = self.gui.grids[id]
            for tag in ('aids', 'm_aids', 'marker', 'preview', 'error'):
                grid.delete(tag)
#        self.eph.start_preview_actions = []  # click action will append
#        self.eph.drag_actions = []           # items to these lists

    def close_action(self, *ids):
        self.close_action_partial(*ids)
        self.eph.start_preview_actions = []  # click action will append
        self.eph.drag_actions = []           # items to these lists
        self.eph.action_string = 'Misc. Action'
        self.eph.action_done = 1
        self.eph.warnings = {}
        self.temp.recovery_state = None
        for grid in self.gui.grids:
            grid.delete('infer')
            grid.delete('infer2')
            grid.delete('visit')
        self.eph.prev_posn = -1,-1
        self.eph.init_posn = -1,-1
        self.eph.init_corners = ()
        if not self.perm.final:
            if self.sess.key_navigation:
                self.eph.est_cell_num_key = 0
                self.adjust_word_number(1 - self.sess.next_focus,
                                        0, see_index=1)
            else:
                self.refresh_num_est()

    def refresh_num_est(self):
        location = self.find_grid_cell()
        if location:
            self.eph.est_cell_num = 0
            self.eph.keep_est_cell_num = 0
            self.move_infer_number(*location)
        elif self.eph.wordbox_yview:
            for d in 0,1:
                self.gui.wordbox[d].yview_moveto(self.eph.wordbox_yview[d])
            self.eph.wordbox_yview = None

    def refresh_save_time_status(self):
        self.master.after_cancel(self.eph.save_time_id)
        self.gui.save_time_msg['fg'] = \
            custom_red if self.need_to_save() else text_fg_color

    # Followup actions have the form (priority, function, arguments).

    def perform_followup_actions(self):
        action_list = self.eph.followup_actions
        action_list.sort()
        self.eph.followup_actions = []
        for pri, action, args in action_list:       # actions added by
            action(*args)                           # handlers as needed
        self.eph.followup_actions = []

    def update_word_counts(self):
        for dir in (0,1):
            self.gui.word_count[dir].configure(
                text='%d / %d' % self.current_word_count(dir))

    def emit_warnings(self):
        if not self.eph.warnings: return
        cum_msgs = []
        for w in self.eph.warnings.items():
            title, msg = warning_messages[w[0]]
            if w[1] != 1:
                msg = msg % w[1]   # message has arguments
            cum_msgs.append('[ %s ]  %s' % (title, msg))
            log_user_message(title, msg)
        self.eph.temp_msg_id = \
            show_temp_msg_panel(cum_msgs, self.eph.temp_msg_id,
                                self.gui.temp_msg_panel)

    def close_temp_displays(self):
        self.gui.temp_msg_panel[2]()    # hide_panel()
        if self.sess.focus_region >= 2:
            self.gui.grids[self.sess.focus_region - 2].delete('visit')


# ---------- Word panel events ---------- #

# Generate procedures used as event handlers for word panels.  These will be
# bound to the Enter button/key, the Delete button, and the selection event.

    def word_event_handlers(self, dir):
        def enter_proc(dummy=None):           # Enter key/button
            if self.eph.preview > 0:
                self.key_release_move()   # key move in progress -- finish it
                return
            # look up id, row, col from mouse cursor position
            location = self.find_grid_cell()[1:]
            if location:
                # give key cursor priority over mouse cursor:
                if self.sess.key_navigation:
                    id = location[0]
                    row, col = self.temp.key_cursors[id][1:3]
                else:
                    id, row, col = location
            else:
                id, row, col = None, None, None
            try:
                num, word, alts, n_ent, w_ent = \
                    self.look_up_entry(dir, id, row, col)
            except UserError:
                if location: self.close_action(location[0])
                return           # parse error, no restoration needed
            self.eph.last_word[dir] = (num, word) # save for recall entry event
            self.start_action()
            try:
                if location:
                    if self.perm.posns[id][dir].get(num) == (row,col) \
                       and not w_ent:
                        # merge crossing letters when recalling same word
                        word = self.merge_with_crossing(dir, word,
                                                        id, row, col)
                self.insert_num_word_cmd(dir, num, word, 1, id, row, col,
                                         alts=alts)
                new_num, index = self.next_number(dir, num, 1)
                self.temp.next_word_num[dir] = new_num      # autoincrement
                if id != None and self.sess.key_navigation:
                    # advance key cursor (same as Tab command)
                    if dir: self.move_key_cursor(id, 1, 0, 1, seek=1)
                    else:   self.move_key_cursor(id, 0, 0, 4)
                self.set_listbox_indicator(dir, new_num, index, # save_new=1,
                                           see_index=1)
                self.finish_action(dir, id)
            except UserError:
                self.restore_state(id)
            self.gui.word_ent[dir].focus_set()

        def delete_proc(dummy=None):            # Delete button
            fields = string.split(self.gui.word_ent[dir].get())
            if not fields: return
            try:
                sel = int(fields[0])
            except ValueError:
                user_dialog(showerror, *error_messages['empty_deletion'])
                return
            if sel not in self.perm.nums[dir]:
                user_dialog(showerror,
                            *error_msg_sub('nonexistent_deletion', sel))
                return
            self.start_action()
            self.del_word_all(dir, sel)
            self.gui.word_ent[dir].focus_set()
            self.finish_action(dir, None)

        def select_proc(event):                 # item selection
            for d in (0,1): self.gui.word_ent[d].delete(0, END)
            wordbox = self.gui.wordbox[dir]
            wordbox.selection_clear(0, END)
            index = wordbox.nearest(event.y)
            if index < 0:
                return                          # empty listbox
            center_word_view(self.gui.wordbox[dir], index, 0.45)
            self.gui.next_num[dir].config(text='')

            item = wordbox.get(index)[0]
            num = item[0]
            symb, word = item[1].split(clue_separator)[0].split()
            if word == null_word_symb: word = ''
            word = word.split(',')[0]   # strip off alternates indicator
            num_word_string = '%s %s' % (num, word)
            self.gui.word_ent[dir].insert(0, num_word_string)
            self.sess.word_entry_text[dir] = num_word_string
            self.set_listbox_indicator(dir, int(num), index)
            wordbox.selection_set(index) #####
            # selection index matches perm.nums index only in clueless mode:
            snw_index = None if self.temp.puz_defn else index
            self.temp.sel_num_word[dir] = (int(num), word, snw_index)
            self.gui.status_line2['text'] = \
                '%s-%s :  %s letters' %  (num, dir_text[dir], len(word))

        return map(EventHandler,
                   map(lambda event: '%s %s' % (event, dir_text[dir]),
                       ('Enter key/button', 'Delete button',
                        'Wordbox selection')),
                   (enter_proc, delete_proc, select_proc))


# ---------- Mouse motion events ---------- #

# While waiting for user input, track mouse motion on grid.  Every time
# it moves to a new cell, check if a word number can be inferred.

    def track_with_indicators(self, id, dir, drow=None, dcol=None):
        # dir = 0,1 for one dir; 2 for both
        # move indicators if present; otherwise, create one/two
        num_row, num_col = self.gui.indicators[id]
        if drow == None:
            # create indicator, either dir
            self.gui.create_indicators[id](dir)
            return
        if not (num_row or num_col):
            # create one or both indicators
            self.gui.create_indicators[id](dir)
        if dir > 0:            # column move
            if num_col:
                num_col.move('indic', dcol*cell_size, 0)
                num_col.move('bar',   dcol*cell_size, 0)
        if dir != 1:           # row move
            if num_row:
                num_row.move('indic', 0, drow*cell_size)
                num_row.move('bar',   0, drow*cell_size)

    def move_quiescent_xy(self, id, ex, ey, x, y):
        # mouse motion without dragging an object
        self.eph.event_xy = (ex, ey)
        self.move_quiescent(id, y // cell_size, x // cell_size)

    def move_quiescent(self, id, row, col):
        if self.perm.final: return
        if not (0 <= row < grid_size[id] and
                0 <= col < grid_size[id]):    # off the canvas
            return
        row0,col0 = self.eph.prev_posn
        self.eph.prev_posn = row,col
        if (row0,col0) == (row,col): return   # still in same cell
        dir = 1 - self.sess.next_focus
        if row0 < 0: drow, dcol = None, None
        else:        drow, dcol = row - row0, col - col0
        self.track_with_indicators(id, dir, drow, dcol)
            
        # note if user has changed number, then moved within same row/col
        keep = self.eph.keep_est_cell_num and (not dir and row0 == row)
        if not self.sess.key_navigation:
            try:
                self.move_infer_number(self.gui.grids[id], id,
                                       row, col, keep, 1)
            except:
                pass  # ignore issues from destroyed widgets & similar events

# Dragging of mouse cursor during preview mode causes all canvas objects
# with tag 'preview' to be advanced by dx,dy (quantized by cell_size).
# Any additional drag actions are also invoked.

    def move_preview_action(self, id, row, col):
        row0,col0 = self.eph.prev_posn
        if (row0,col0) == (row,col): return   # still in same cell
        if row0 < 0:
            # recover true values if cursor is returning to canvas
            row0 += 1000; col0 += 1000
        drow, dcol = row - row0, col - col0
        self.track_with_indicators(id, 2, drow, dcol)
        self.gui.grids[id].delete('m_aids')    ###
        self.gui.grids[id].move('preview', dcol*cell_size, drow*cell_size)
        for action in self.eph.drag_actions:  # actions added by
            action(id, row, col)              # handlers as needed

# In mouse navigation mode, cells are "visited" (after a delay), which
# causes inferred numbers and words to be displayed.

    def move_infer_number(self, grid, id, row, col,
                          keep_num=0, delay_factor=0):
        if not keep_num: self.eph.est_cell_num = 0
        if self.eph.preview:
            return     # suppress inference during dragging
        grid.after_cancel(self.eph.visit_id)
        grid.after_cancel(self.eph.scroll_id)
        grid.delete('infer')
        grid.delete('visit')
        dir = 1 - self.sess.next_focus

        def visit_cell_infer_num():
            entry_num = parse_number(self.gui.word_ent[dir].get())[0]
            if entry_num > 0:
                self.eph.est_cell_num = entry_num
                self.eph.keep_est_cell_num = 0
                self.show_inferred(grid, id, dir, row, col, entry_num, 1)
                return       # suppress if user is typing a word number
            if keep_num and self.eph.est_cell_num:
                # user changed number with +/- then moved within same row
                self.show_inferred(grid, id, dir, row, col,
                                   self.eph.est_cell_num)
                return    # no need to scroll listbox
            try:
                num = self.infer_word_number(dir, id, row, col)       ###
                self.eph.est_cell_num = num
                self.eph.keep_est_cell_num = 0   # indicate subject to change
                self.show_inferred(grid, id, dir, row, col, num)
                delayed_proc = \
                    lambda *args: self.scroll_listbox(dir, num, id, row, col)
            except OffNominal:
                delayed_proc = lambda *args: self.scroll_listbox_xy()
                self.gui.status_line2['text'] = ''

            self.eph.scroll_id = \
                grid.after(scroll_delay * delay_factor,
                           EventHandler('Grid move infer scroll',
                                        delayed_proc))

        self.adjust_temp_word_display(dir, self.gui.word_ent[dir].get())
        self.eph.visit_id = \
            grid.after(visit_delay * delay_factor,
                       EventHandler('Grid move infer visit',
                                    visit_cell_infer_num))

    def show_inferred(self, grid, id, dir, row, col, num, force=0):
        if self.eph.multistep_mode: return
        # display inferred word number and word, if available
        cells = self.aux.cells[id]
        interior = (self.eph.event_xy[0] >= cell_size,  # not leftmost column
                    self.eph.event_xy[1] >= cell_size)  # not top row
        word_ent = self.gui.word_ent[dir].get()
        if word_ent:
            self.adjust_temp_word_display(dir, word_ent)
            # painting number needs to follow temp word so number lies on top
            paint_inferred_number(grid, cells, dir, row, col, 'infer',
                                  num, num in self.perm.nums[dir],
                                  interior, force)
            return
        if num:
            self.show_inferred_word(id, dir, row, col, num, pointer=1)
        paint_inferred_number(grid, cells, dir, row, col, 'infer',
                              num, num in self.perm.nums[dir],
                              interior, force)

    def show_inferred_word(self, id, dir, row, col, num, pointer=0):
        try:
            word = self.perm.words[dir][num]
            if self.perm.posns[id][dir].get(num) != (row, col):
                # don't paint if same word and position
                self.paint_word_temp(id, dir, word, '', row, col,
                                     ('visit',), offset=1, pointer=pointer)
        except KeyError:
            pass   # OK: no word for this number


# ---------- Mouse click events ---------- #

# Button 1 actions are performed on button-up events.  Some actions have a
# preview mode that is initiated at button-down plus short delay.  The same
# procedure is invoked for those two events; they distinguish state via
# sess.preview and sess.action_done.  Dragging the mouse causes motion
# events that may be responded to.

    def grid_click_1(self, id, x, y, shift=0):     # action varies by mode
        # ignore event if popup menu now unposting (Windows)
        if self.eph.popup_posting:
            return
        grid = self.gui.grids[id]
        if self.eph.multistep_mode:
            grid.delete('preview')    # remove first-step highlighting
        self.eph.preview = 1
        row, col = y // cell_size, x // cell_size
        self.eph.init_posn = row, col

#        # click action will add items to following lists:
#        self.eph.start_preview_actions = []
#        self.eph.drag_actions = []
        paint_cell_marker(grid, row, col)
        def start_preview():
            for action in self.eph.start_preview_actions: action(id)
            map_posn = self.gui.map_grid_posn[id]
            self.eph.prev_posn = row, col
            for action in self.eph.drag_actions:  # actions added by
                action(id, row, col)              # handlers as needed
            def move_preview(event):
                self.eph.preview += 1
                if self.eph.action_done: return
                ex, ey = map_posn(event.x, event.y)
                erow, ecol = ey // cell_size, ex // cell_size
                if 0 <= erow < grid_size[id] and \
                   0 <= ecol < grid_size[id]:      # on the canvas
                    self.move_preview_action(id, erow, ecol)
                    self.eph.prev_posn = erow, ecol
            wrapped_bind(grid, '<B1-Motion>', move_preview,
                         'Grid %d preview motion' % id)
        self.eph.preview_id = \
            grid.after(preview_delay,
                       EventHandler('Grid %d start preview' % id,
                                    start_preview))
        # next_click_action is set by handlers to catch future clicks
        if shift:
            self.start_action()
            self.paste_word_shift(id, row, col)
        else:
            if self.sess.key_navigation:
                # setting the key cursor => only a pseudo-action
                self.eph.action_done = 0
            else:
                # in mouse nav mode => starting a real action
                self.start_action()
            self.sess.next_click_action(id, row, col)

    def grid_click_1_shift(self, id, x, y):      # move region
        self.grid_click_1(id, x, y, shift=1)

    def grid_click_1_up(self, id, x, y):         # action varies by mode
        # reset flag and ignore if popup menu now unposting (Windows)
        if self.eph.popup_posting:
            self.eph.popup_posting = 0
            return
        # ignore spurious events (down event sets eph.preview)
        if self.eph.preview == 0: return

        row, col = y // cell_size, x // cell_size
        grid = self.gui.grids[id]
        grid.after_cancel(self.eph.preview_id)
        grid.unbind('<B1-Motion>')   ### add funcid for deletion
        for tag in ('preview', 'marker', 'm_aids'):
            grid.delete(tag)
        self.eph.preview = 0
        self.eph.drag_actions = []
        # marks new location in case of error:
        paint_cell_marker(self.gui.grids[id], row, col)
        multi_mode = self.eph.multistep_mode
        if not self.eph.action_done:
            self.sess.next_click_action(id, row, col)
        if multi_mode and not self.eph.multistep_mode:
            # a multistep action just finished; refresh cursor/cue
            if self.sess.key_navigation:
                self.set_key_cursor(self.temp.key_cursors[id][1:3])
            else:
                dir = 1 - self.sess.next_focus
                self.adjust_word_number(dir, 0, delay_factor=1)


# Right clicks lead to one of two sequences.  If the up-event follows
# the down-event quickly, the action is to toggle the entry focus.
# Otherwise, a popup menu is displayed and the user may choose an
# action from the menu.  Some of those actions might be multistep
# operations that will be completed after subsequent left clicks
# are performed.

    def grid_click_2(self, id, x, y):         # right click toggle or popup
        if self.eph.multistep_mode: return    # ignore if already busy
        self.eph.init_posn = row, col \
                           = y // cell_size, x // cell_size
        self.eph.popup_args = None            # stays None if popup aborted
        def display_popup():
            self.eph.popup_args = (id, row, col)  # needed by action procs
            grid = self.gui.grids[id]
            sx = grid.winfo_rootx() + (col+1)*cell_size - 6 - \
                 int(grid.canvasx(0))
            sy = grid.winfo_rooty() + (row+1)*cell_size - 6 - \
                 int(grid.canvasy(0))
            dir = 1 - self.sess.next_focus
            self.gui.popup[dir].tk_popup(sx, sy)
        self.eph.popup_id = \
            self.gui.grids[id].after(app_prefs['popup_delay'],
                EventHandler('Grid %d popup' % id, display_popup))

# Following binding doesn't fire after a popup menu is displayed.  It's
# only used to change working direction.

    def grid_click_2_up(self, id, x, y):      # toggle direction
#        if not self.eph.popup_args:           # only if no popup occurred
#            self.gui.create_indicators[id]()  # change indicator triangle
        if self.eph.multistep_mode:
            return                            # ignore rest if already busy
        self.gui.grids[id].after_cancel(self.eph.popup_id)
        if not self.eph.popup_args:
            self.toggle_entry_focus()         # only if no popup occurred
            self.gui.create_indicators[id]()  # change indicator triangle
        self.eph.popup_posting = 0
        
    def restore_click_action(self):           # used after multistep actions
        dir = 1 - self.sess.next_focus
        self.eph.multistep_mode = 0
        self.set_grid_cursors(dir)
        self.sess.next_click_action = self.sess.default_click_action

# Provide explicit popup action for Mac if ctrl-button-1 unavailable.

    def display_grid_popup(self, id, row, col):   # simulate right click
        if self.eph.multistep_mode: return        # ignore if already busy
        self.eph.popup_args = (id, row, col)      # needed by action procs
        grid = self.gui.grids[id]
        sx = grid.winfo_rootx() + (col+1)*cell_size - 6 - int(grid.canvasx(0))
        sy = grid.winfo_rooty() + (row+1)*cell_size - 6 - int(grid.canvasy(0))
        dir = 1 - self.sess.next_focus
        self.gui.popup[dir].tk_popup(sx, sy)


# ---------- Special key events ---------- #

# Following methods are for posting and moving key cursors.  They are
# invoked by the various key-cursor commands.

# Create a fresh key cursor, either in response to an event or as
# part of a direction toggling action.

    def set_key_cursor(self, posn=None, event=None, adjust=1):
        if not self.sess.key_navigation: return  # key mode disabled
        if self.sess.focus_region < 2: return    # not over a grid
        if self.perm.final: return               # suppress if finalized
        if posn:
            id = self.sess.focus_region - 2
            row, col = posn
        else:
            location = self.find_grid_cell()
            if location:
                grid, id, row, col = location
            else:
                return    # can't find position
        dir = 1 - self.sess.next_focus
        canv = self.gui.grids[id]

        # Can be called on Button down and up events.  Check for
        # direction-changing mouse gesture.
        if event == 'up':
            self.adjust_temp_word_display(dir, self.gui.word_ent[dir].get())
            self.eph.action_done = 1
            return
        elif event == 'down':
            canv.delete('marker')    # no marker needed with key cursor
            self.start_key_cursor_drag(dir, id, canv, row, col)

        next = self.next_free_cell(id, dir, row, col, delta=0)
        if not next: return    # can't find a cell; need an exception?
        row, col = next
        canv_obj = paint_key_cursor(canv, dir, row, col, 'letter')
        self.temp.key_cursors[id] = (canv_obj, row, col)
        if adjust:
            self.eph.est_cell_num_key = 0
            self.adjust_word_number(dir, 0, see_index=1, delay_factor=1,
                                    location=(canv, id, row, col))

    def start_key_cursor_drag(self, dir, id, grid, row0, col0):
        def place_key(id, erow, ecol):
            if dir == 1 and erow == row0 and ecol > col0 or \
               dir == 0 and ecol == col0 and erow > row0:
                # transition detected; toggle direction and remove bindings
                # must remove bindings here to prevent more toggle actions
                self.toggle_entry_focus((grid, id, erow, ecol))
                del self.eph.drag_actions[-1]
        self.eph.drag_actions.append(place_key)


# Move grid cursor in response to key commands.  Normal deltas are
# +/- k.  Larger magnitudes come from Tab bindings.  If move_dir > 1,
# use value of current direction.  Some events (Left, Right, Tab, Shift-Tab)
# have standard bindings we'd like to avoid.  The stop arg is used to signal
# a break so these bindings can be skipped.

    def move_key_cursor_event(self, move_dir, change_dir, delta, stop=0):
        signal = 'break' if stop else None
        if self.perm.final: return signal          # suppress if finalized
        if self.eph.preview > 0:
            # print 'move-grid-cursor' #####
            # # key move in progress
            # if move_dir > 1: return signal   # ignore Tab chars here
            # self.move_key_preview(move_dir * delta, (1 - move_dir) * delta)
            return signal
        id = self.sess.focus_region - 2
        if id < 0: return    # not over a grid
        dir = 1 - self.sess.next_focus
        if move_dir > 1:
            move_dir = dir
        elif change_dir and dir != move_dir:
            # when changing direction, the first arrow char event
            # rotates the cursor but doesn't advance it
            self.toggle_entry_focus()
            return signal
        self.move_key_cursor(id, dir, move_dir, delta)
        return signal

# Move key cursor in move_dir while working direction is dir.  If seek
# flag is on, look for next feasible cell (for current dir).

    def move_key_cursor(self, id, dir, move_dir, delta, seek=0):
        canv = self.gui.grids[id]
        cells = self.aux.cells[id]
        canv_obj, cur_row, cur_col = self.temp.key_cursors[id]
        next = self.next_free_cell(id, move_dir, cur_row, cur_col, delta)
        prev = None
        # Need to break out of loop if next becomes a repeating sink value,
        # in which case no cursor movement will occur.
        while next and next != prev:
            row, col = prev = next
            if seek and dir:
                cell = row > 0 and cells[row-1][col]
                if cell and (cell[0] or cell[1]):
                    next = self.next_free_cell(id, move_dir, row, col, 1)
                    continue
                try:
                    if cells[row+1][col][2] or cells[row+2][col][2]:
                        next = self.next_free_cell(id, move_dir, row, col, 1)
                        continue
                except IndexError:
                    pass    # near end of column -- need to use it
            dx, dy = (col - cur_col) * cell_size, (row - cur_row) * cell_size
            canv.move(canv_obj, dx, dy)
            self.temp.key_cursors[id] = (canv_obj, row, col)
            canv.delete('infer2')
            if self.eph.preview == 0:
                # don't perform following during drag/preview actions
                self.adjust_temp_word_display(dir, self.gui.word_ent[dir].get())
                self.eph.est_cell_num_key = 0
                self.adjust_word_number(dir, 0, see_index=1, delay_factor=1,
                                        location=(canv, id, row, col))
            break

    def show_inferred_key(self, grid, id, dir, row, col, num, force=0):
        # display inferred word number and word, if available
        interior = (col > 0,  # not leftmost column
                    row > 0)  # not top row
        word_ent = self.gui.word_ent[dir].get()
        if word_ent:
            self.adjust_temp_word_display(dir, word_ent)
        # painting number needs to follow temp word so number lies on top
        paint_inferred_number(grid, self.aux.cells[id], dir, row, col,
                              'infer2', num, num in self.perm.nums[dir],
                              interior, force)
        if word_ent:
            return
        if num:
            grid.after_cancel(self.eph.key_visit_id)
            self.show_inferred_word(id, dir, row, col, num)
            # for key nav case, only show inferred word for a few seconds
            self.eph.key_visit_id = \
                grid.after(temp_word_delay,
                           EventHandler('Clear temp word',
                                        lambda : grid.delete('visit')))
