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

class DiagWordGrid(object):
    def __init__(self, master=None): pass


# ---------- Word list entry and grid pasting ---------- #

# Normal action for clicking on a grid cell.  The current word-entry
# widget is checked.  The entry text is parsed, its contents
# inserted into the data structures and then pasted on the grid.  If no
# word entry, then check for other possibilities, such as grabbing the
# letters of crossing words.  Otherwise, ignore.  Do setup so that if
# preview is initiated, a preview form of word will be displayed.

    def paste_word(self, id, row, col):
        # start_action performed in grid_click_1 (diag_events)
        dir = 1 - self.sess.next_focus
        if self.eph.preview == 1:
            # in key mode, clicks will set key cursor
            if self.sess.key_navigation:
                # set cursor unconditionally for click in key mode
                self.set_key_cursor(event='down')
                self.eph.num_word = 'set_cursor'   # for button-up event
                return
            try:
                num, word, alts, n_ent, w_ent = \
                     self.look_up_entry(dir, id, row, col, 1)    ### excep
            except UserError:
                return
            def show_first_word(id_to):
                # create word in preview form only once
                self.insert_num_word_first(dir, num, word, 1, id_to, row, col)
                self.gui.create_indicators[id](2, (row, col))
            self.eph.start_preview_actions.append(show_first_word)
            # save for button-up event
            self.eph.num_word = (num, word, alts, n_ent, w_ent)
            self.eph.init_posn = self.perm.posns[id][dir].get(num, (-1,-1))
        else:
            if self.eph.num_word == 'set_cursor':
                self.set_key_cursor(event='up')
                self.eph.num_word = None
                self.close_action_partial(id)    # no word, no effects on perm
                return
            elif not self.eph.num_word:
                self.close_action(id)    # no word, no effects on perm
                return
            num, word, alts, n_ent, w_ent = self.eph.num_word
            self.eph.num_word = None
            if self.eph.init_posn == (row, col) and not w_ent:
                # merge crossing letters when recalling same word
                word = self.merge_with_crossing(dir, word, id, row, col)
            try:
#                if word == self.perm.words[dir].get(num):
#                    alts = None     # selection and pasting of existing word
                self.insert_num_word_cmd(dir, num, word, 1, id, row, col,
                                         alts=alts)
                new_num, index = self.next_number(dir, num, 1)
                self.temp.next_word_num[dir] = new_num   # autoincrement
                self.set_listbox_indicator(dir, new_num, index)
                self.eph.last_word[dir] = (num, word) # for recall entry action
                if self.sess.key_navigation:
                    # advance key cursor (same as Tab command (Across) or
                    # Shift-right (Down) ); follow word number order;
                    if dir: self.move_key_cursor(id, 1, 0, 1, seek=1)
                    else:   self.move_key_cursor(id, 0, 0, 4)
                self.save_action_string('Enter Word', num, dir)
                self.finish_action(dir, id)
            except UserError:
                self.restore_state(id)

# Word and region movement commands (via shift-click) come here.

    def paste_word_shift(self, id, row, col):
        dir = 1 - self.sess.next_focus
        region_mode = self.set_up_region_dragging(dir, id, row, col)
        if not region_mode:
            # parse error or ignoreable event, no restoration needed
            self.close_action(id)
            self.eph.num_word = None   # clear for button-up event
            ### click-up event doesn't fire after
            ### exception during click-down event => reset flag
            self.eph.preview = 0

# Determine whether cell is eligible to select a word region for dragging.
# Returns:  0 - not eligible
#           1 - region dragging set up

    def set_up_region_dragging(self, dir, id, row, col):
        if self.gui.word_ent[dir].get():
            return 0        # inhibit if any text in word entry
        posns = self.perm.posns[id]
        cells = self.aux.cells[id]
        this_cell = cells[row][col]
        if this_cell[2]: 
            # cell occupied by block -> move whole grid
            start = self.start_all_words_translation
        elif this_cell[dir] and \
                posns[dir].get(this_cell[dir][0]) == (row, col):
            # cell has a letter in the given direction and 
            # the position of the cell's word number matches row, col ->
            # this is a head cell so we move one word only
            start = self.start_single_word_translation
        elif this_cell[1-dir] and \
                posns[1-dir].get(this_cell[1-dir][0]) == (row, col):
            # head cell in the other direction -> move one word
            start = self.start_single_word_translation
        elif this_cell[0] or this_cell[1]:
            # cell has at least one letter -> move adjacent words
            start = self.start_adjacent_words_translation
        else:
            return 0    # otherwise, no valid movement was selected

        def show_first_region(id_to):
            ### using id_to ???
            # create region in preview form only once
            # emulate multistep sequence
            start(id, row, col)
            self.sess.next_click_action(id, row, col)
#            self.gui.create_indicators[id](2, (row, col))
            # start procedures normally set for multistep
            self.eph.multistep_mode = 0
        self.eph.start_preview_actions.append(show_first_region)
        return 1


# First step of insertion process is to delete word from any canvas
# on which it resides, then display preview of word in new location.

    def insert_num_word_first(self, dir, num, word, adjust,
                              id=None, row=None, col=None, check=2,
                              alts='', show_alts=1):
        try:
            old_id = self.perm.grid_id[dir][num]
            grid_posn = self.perm.posns[old_id][dir][num]
            self.del_word_grid(old_id, dir, *grid_posn)
        except KeyError:
            pass
        self.insert_num_word_pre(dir, num, word, 1, id, row, col)
        if dir:
            self.eph.init_corners = (0, 0, len(word), 1)
            self.eph.drag_words = [[], [(0, 0, len(word))]]
        else:
            self.eph.init_corners = (0, 0, 1, len(word))
            self.eph.drag_words = [[(0, 0, len(word))], []]
        self.eph.drag_actions.append(self.check_dragging_words)

# Preview form just paints the word without making any state changes.  Keep
# arguments the same as insert_num_word even though some are not used.

    def insert_num_word_pre(self, dir, num, word, adjust,
                            id=None, row=None, col=None, check=2,
                            alts='', show_alts=1):
        self.paint_word_pre(id, dir, word, row, col,
                            ('preview',), preview_color)
        for r,c in end_blocks(grid_size[id], dir, len(word), row, col):
            self.paint_block(id, r, c, ('preview',), block_pre_color)

# The full details of insertion are complicated by checking for an
# existing word and deleting it if present.  Insertion on one grid removes
# that word from another; a word appears on one grid at most.  If no row
# or grid id is specified, reuse old values when applicable.  Listbox
# maintenance is conducted after grid operations.  Argument 'check' is 2
# for error checks plus auto-completions and 1 for just error checks.

    def insert_num_word(self, dir, num, word, adjust, id=None,
                        row=None, col=None, check=2, alts=[], show_alts=1):
        # Requires: row != None implies id != None;
        # alts is a list of alternative words
        # or None to suppress alts processing.
        self.check_non_puz_defn_num(dir, num)                       ### excep
        selection = self.temp.sel_num_word[dir]  # (num, word, index)
        sel_word = None
        if selection:
            # If a selection was renumbered, delete the old-number version
            if num != selection[0] and word == selection[1] and \
               self.perm.words[dir].has_key(selection[0]):
                sel_word = self.del_word_all(dir, selection[0], selection[2])
        elif check:
            self.word_overwrite_check(dir, num, word)
        posns = self.perm.posns

        # If word is currently on a grid, get location and delete it
        try:
            old_id = self.perm.grid_id[dir][num]
            grid_posn = posns[old_id][dir][num]
            if id == None:  id = old_id          # if no grid or row requested,
            if row == None:                      #   reuse existing place
                row,col = grid_posn
                old_word = self.perm.words[dir][num]
                # move start of word when lengths differ and tails match
                if not word.startswith(old_word[:3]) and \
                    word.endswith(old_word[-3:]) :
                    dlen = len(word) - len(old_word)
                    if dir: row = max(0, row - dlen)
                    else:   col = max(0, col - dlen)
            self.del_word_grid(old_id, dir,      # wipe old word off its grid
                               *grid_posn)
        except KeyError:
            if sel_word and id == None and row == None:
                id,row,col = sel_word

        # Check for conflicts before grid placement
        if row != None:
            if check:
                # must catch grid overflows before any other checking
                self.check_grid_overflow(dir, word, id, row, col)  ### excep
                # check if new word crosses any end blocks
                for n,w,r,c in \
                    self.cross_extensions(dir, word, id, row, col): ### excep
                    # extend crossing words with letters from new word
                    self.insert_num_word(1-dir, n, w, 0, id, r, c, 0)
                # crossing extensions should precede the conflict check so
                # resolvable conflicts are handled first
                self.check_conflict(dir, word, num, id, row, col)  ### excep
                self.head_cell_mismatch(dir, num, id, row, col)    ### excep
                self.word_out_of_order(num, id, row, col)          ### warning
            if id > 0: gridded = '#'
            else:      gridded = '+'
            acquired_word = self.paint_word(id, dir, num, word, row, col)
        else:
            gridded = '-'
            acquired_word = word

        if acquired_word == self.perm.words[dir].get(num):
            alts = None     # selection and pasting of existing word
        self.perm.words[dir][num] = acquired_word
        index = self.update_listbox_item(dir, num, gridded, acquired_word,
                                         insert_num=1, word_alts=alts,
                                         show_alts=show_alts)
        if id != None and row != None:
            self.append_blocks(dir, len(acquired_word), id, row, col)
        if row != None and check == 2:
            self.check_word_completions(dir, len(acquired_word), id, row, col)
        if adjust and id != None and row != None:
            self.adjust_wordboxes(id, row, col)
        elif adjust:
            center_word_view(self.gui.wordbox[dir], index, 0.45)
        if adjust:
            self.gui.status_line['text'] = \
                '%s-%s :  %s' % (num, dir_text[dir], acquired_word)
            self.duplicate_word_check(dir, num, acquired_word)    ### warning

    def insert_num_word_cmd(self, dir, num, word, adjust, id=None,
                            row=None, col=None, check=2,
                            alts=[], show_alts=1):
        self.insert_num_word(dir, num, word, adjust, id, row, col,
                             check=check, alts=alts, show_alts=show_alts)
        self.save_action_string('Enter Word', num, dir)

    def check_word_completions(self, dir, wlen, id, row, col):
        # call only after a word and its end blocks are in place;
        # first check possible crossing words of this word's letters
        crossing = self.cross_completions(dir, wlen, id, row, col)

        # next try cells left/above and right/below end blocks for possible
        # adjacent words aligned in the crossing direction
        size = grid_size[id]
        dr, dc = -1, -1
        for dd in ((2, 0), (0, wlen+1), (-2, 0), (0, 0)):
            if 0 <= row + dr < size and 0 <= col + dc < size:
                crossing.extend(
                    self.cross_completions(dir, 1, id, row + dr, col + dc))
            dr += dd[dir]; dc += dd[1-dir]

        for n,w,r,c in crossing:
            # add a new word; schedule later update to avoid
            # inconsistent states; use num as priority
            self.eph.followup_actions.append(
                (n, self.insert_auto_completion, (1-dir, n, w, id, r, c)))

        # next try cells before and after end blocks for possible
        # adjacent words aligned with this direction
        aligned = []
        dr, dc = 2 * dir, 2 * (1-dir)
        if 0 <= row - dr and 0 <= col - dc:
            aligned.extend(
                self.cross_completions(1-dir, 1, id, row - dr, col - dc))
        dr, dc = (wlen + 1) * dir, (wlen + 1) * (1-dir)
        if row + dr < size and col + dc < size:
            aligned.extend(
                self.cross_completions(1-dir, 1, id, row + dr, col + dc))

        for n,w,r,c in aligned:
            self.eph.followup_actions.append(
                (n, self.insert_auto_completion, (dir, n, w, id, r, c)))

    def insert_auto_completion(self, dir, n, word, id, row, col):
        # recompute inferred number after each preceding insertion
        # to get a more accurate estimate
        try:
            num = self.infer_word_number(dir, id, row, col, need_unique=1)
        except OffNominal:
            return 0        # this word no longer viable
        if num:
            self.insert_num_word(dir, num, word, 0, id, row, col, 0) # check?
            return 1
        return 0


# ---------- Word list and grid management ---------- #

# "Rotating" a word means moving it from Across to Down or vice versa.
# If it appears on a grid, it will be rotated (pivoted) by 90 degrees.

    def rotate_word(self):
        dir = 1 - self.sess.next_focus
        # look up id, row, col from mouse cursor position
        location = self.find_grid_cell()[1:]
        try:
            num, word, alts, n_ent, w_ent = self.look_up_entry(dir, *location)
        except UserError:
            return           # parse error, no restoration needed
        if self.perm.words[dir].has_key(num):
            self.start_action()
            try:
                id = self.perm.grid_id[dir][num]
                row,col = self.perm.posns[id][dir][num]
            except KeyError:   # raised if word not found on grid
                id,row,col = None,None,None
            self.del_word_all(dir, num)
        else:
            user_dialog(showerror, *error_msg_sub('rotate_word_missing',
                                                  (num, dir_text[dir])))
            return
        try:
            self.insert_num_word_cmd(1-dir, num, word, 1, id, row, col)
            self.finish_action(dir, id)
        except UserError:
            self.restore_state(id)

# Delete a word from both grid and listbox.  Word num must exist.

    def del_word_all(self, dir, num, index=None):
        result = None
        if index == None:
            # assumes num appears in perm.nums:
            index = bisect_left(self.perm.nums[dir], num)
        try:
            id = self.perm.grid_id[dir][num]
            row,col = self.perm.posns[id][dir][num]
            result = self.del_word_grid(id, dir, row, col)
        except KeyError:
            pass    # word not on a grid -> benign
        word = self.perm.words[dir][num]
        del self.perm.words[dir][num]
        del self.perm.nums[dir][index]
        if self.temp.puz_defn:
            # includes deletion of alt words:
            self.update_listbox_item(dir, num, '-', null_word_symb)
        else:
            try:
                del self.perm.alt_words[dir][num]
            except KeyError:
                pass     # word had no alternates
            self.gui.wordbox[dir].delete(index)
        self.gui.status_line['text'] = \
            "%s-%s '%s' has been deleted." % (num, dir_text[dir], word)
        self.save_action_string('Delete Word', num, dir)
        return result

    def del_word_all_action(self, dir, id, row, col): # For use in popup menu
        # start_action performed in calling environment
        cell = self.aux.cells[id][row][col]
        if cell[dir] and self.del_word_all(dir, cell[dir][0]) :
            self.finish_action(None, id)
        else:
            self.close_action(id)    # no state change
            
    def del_word_grid_action(self, dir, id, row, col): # For use in popup menu
        # start_action performed in calling environment
        if self.del_word_grid(id, dir, row, col, 1):
            self.finish_action(None, id)
        else:
            self.close_action(id)    # no state change

# Delete a word from the grid but not its listbox.  Cells are updated
# to reflect new vacancies.  The listbox entry is marked as ungridded.
# Return grid id and row,col of word's head cell, or None if no word
# passes through row,col in given direction.
# Clear blocks from both ends of word.

    def del_word_grid(self, id, dir, row, col, update_box=0):
        cells = self.aux.cells[id]
        cell = cells[row][col]
        grid = self.gui.grids[id]
        posns = self.perm.posns[id]
        if cell[dir]:
            grid.delete(cell[dir][1])  # delete word from canvas
            num = cell[dir][0]
            word = self.perm.words[dir][num]
            cross_words = self.perm.words[1-dir]
            wrow,wcol = posns[dir][num]
            for r,c in generate_cells(dir, len(word), wrow, wcol):
                this_letter = cells[r][c][dir][2]
                cells[r][c][dir] = None
                grid.delete(clash_dot_tag(r,c))
                cross_cell = cells[r][c][1-dir]  # cell of crossing word
                if cross_cell:
                    index = self.letter_index(1-dir, id, r, c)
                    cross_letter = cross_words[cross_cell[0]][index]
                    if this_letter != cross_letter or \
                            cross_letter == placeholder:
                        grid.delete(
                            letter_cell_tag(cells[r][c][1-dir][1], r, c))
                        # revert crossing letter display to placeholder or
                        # existing letter in case of clash
                        # schedule later update to avoid inconsistent states
                        # use letter index as priority
                        self.eph.followup_actions.append(
                            (index, self.update_gridded_letter,
                             (1-dir, cross_cell[0], id, cross_letter,
                              index, None)))
            del posns[dir][num]
            del self.perm.grid_id[dir][num]
            # unpaste end blocks *after* clearing cell entries
            self.append_blocks(dir, len(word), id, wrow, wcol, 2)
            if update_box:
                self.update_listbox_item(dir, num, '-', word)
            self.gui.status_line['text'] = \
                "%s-%s '%s' has been unpasted." % (num, dir_text[dir], word)
            self.save_action_string('Unpaste Word', num, dir)
            return (id, wrow, wcol)
        else:
            return None
 
# Update an existing, gridded word by replacing a single letter at
# the indicated cell.  Used to replace a placeholder with a letter or
# vice versa, or to revert a letter clash to a single letter.  Assumes
# that multiple invocations are prioritized by letter index.

    def update_gridded_letter(self, dir, num, id, letter,
                              index, expected_cross, overwrite=None):
        try:
            posn = self.perm.posns[id][dir][num]
        except KeyError:
            return                 # ignore if no longer exists
        row = posn[0] + dir * index
        col = posn[1] + (1-dir) * index
        cells = self.aux.cells[id]
        this_cell = cells[row][col]

        if not overwrite:
            if not expected_cross and this_cell[1-dir] and index > 0:
                return  # deleted (non-head) crossing letter already filled in

        cell_dir = this_cell[dir][:2] + (letter,)
        this_cell[dir] = cell_dir

        word_tag = cell_dir[1]
        cell_tag = letter_cell_tag(word_tag, row, col)
        grid = self.gui.grids[id]
        grid.delete(cell_tag)  # delete existing letter from canvas
        if letter == placeholder:
            color = placeholder_color
        else:
            color = 'black'
        paint_cell(grid, row, col, letter, word_tag,
                   (index==0) and num, 0, color)
        word = self.perm.words[dir][num]
        gword = [ cells[r][c][dir][2]
                  for r,c in generate_cells(dir, len(word), *posn) ]
        new_word = ''.join(gword)   ### lower?
        if id > 0: gridded = '#'
        else:      gridded = '+'
        self.update_listbox_item(dir, num, gridded, new_word)   ### word_alts?


# Renumber a word using the estimated word number displayed in the cell
# currently under the mouse cursor.  If there are words in both directions,
# renumber them both.  Also accept a number field in word entry.

    def renumber_word_action(self, from_popup, id=None, row=None, col=None):
        try:
            cur_dir = 1 - self.sess.next_focus
            new_num = self.get_word_num(cur_dir)   ### OffNominal
        except OffNominal:
            # new word number unavailable => can't renumber
            user_dialog(showerror, *error_messages['renumber_info_missing'])
            self.close_action(id)
            return
        try:
            if id == None:
                user_dialog(showerror, *error_messages['renumber_off_grid'])
                self.close_action(id)
                return
            elif self.sess.key_navigation and not from_popup:
                # try to renumber at key cursor location
                krow, kcol = self.temp.key_cursors[id][1:3]
                self.renumber_word(id, krow, kcol, cur_dir, new_num)
            else:
                # try to renumber at mouse cursor location
                self.renumber_word(id, row, col, cur_dir, new_num)
        except (FalseStart, OffNominal):
            user_dialog(showerror, *error_messages['renumber_info_missing'])
            self.close_action(id)

    def renumber_word(self, id, row, col, cur_dir, new_num):
        if id == None:
            raise FalseStart
        cells = self.aux.cells[id]
        delete_args, insert_args = [], []
        for dir in (0,1):
            cell = cells[row][col]
            if not cell[dir] or cell[2]: continue
            # reject if not a head cell
            if dir:
                if row > 0 and cells[row-1][col][1] : continue
            else:
                if col > 0 and cells[row][col-1][0] : continue
            cur_num = cell[dir][0]
            word = self.perm.words[dir].get(cur_num)
            if word:
                delete_args.append((dir, cur_num))
                insert_args.append((dir, new_num, word, 1, id, row, col, 1))
        if not insert_args: raise FalseStart

        self.start_action()
        try:
            for args in delete_args: self.del_word_all(*args)
            for args in insert_args: self.insert_num_word(*args)
            self.save_action_string('Renumber Word', cur_num, cur_dir)
            self.finish_action(cur_dir, id)
        except UserError:
            self.restore_state(id)

# User has opted to promote an alternative answer and move the
# current answer to the alternative list.

    def swap_alt_word(self, dir, num, word):
        self.start_action()
        try:
            self.insert_num_word_cmd(dir, num, word, 0, check=1)
            self.finish_action(dir, 0)
        except :   ### add list: UserError:
            self.restore_state(None)


# Given new values of num, symb or word, update the corresponding item
# in wordbox.  Requires deleting existing one and inserting a new one.
# Clue is retrieved if one exists.

    def update_listbox_item(self, dir, num, symb, word,
                            insert_num=0, word_alts=[], show_alts=1):
        # word is new word, word_alts is alternative word list;
        # word_alts is set to None to suppress alt updates
        def update_alts(old_word):
            alt_words = self.perm.alt_words[dir]
            cur_alts  = alt_words.get(num, [])
            if word_alts == None:                 # skip alt updates
                if cur_alts: return show_alts and ',...' or ''
                else:        return ''
            if word == null_word_symb:            # clueful word deletion
                if cur_alts: del alt_words[num]
                return ''
            if word in cur_alts: cur_alts.remove(word)
  
            if old_word and word != old_word:
                next_alts = word_alts + [old_word.split(',')[0]] + cur_alts
            else:
                next_alts = word_alts + cur_alts
            if next_alts:
                alt_words[num] = list(set(next_alts))  # remove duplicates
                return show_alts and ',...' or ''
            else:
                return ''      # no alts => no entry in alt_words
            
        puz_defn = self.temp.puz_defn
        if puz_defn: num_lists = puz_defn.nums
        else:        num_lists = self.perm.nums
        num_list = num_lists[dir]
        num_str = str(num)
#        if num in num_lists[1-dir]: num_str += '*' ### future: double-head

        index = bisect_left(num_list, num)
        listbox = self.gui.wordbox[dir]
        if puz_defn:
            try:
                cur_word = listbox.get(index)[0][1] \
                               .split()[1].split(',')[0]   # strip ',...'
            except IndexError:
                cur_word = ''
            suffix = update_alts((cur_word != null_word_symb) and cur_word)
            listbox.delete(index)
            self.insert_with_caching(index, symb, num_str, word + suffix,
                                     puz_defn.clues[dir][index], listbox,
                                     self.temp.wrapped_clues[dir])
            # in clueful mode, perm.nums serves to track words that have
            # been entered, which is a subset of nums in the clue list
            num_list = self.perm.nums[dir]
            if insert_num and num not in num_list:
                num_list.insert(bisect_left(num_list, num), num)
        else:
            clue = ''
            if num_list and index < len(num_list) and num == num_list[index]:
                # a word for num already exists
                cur_word = listbox.get(index)[0][1] \
                               .split()[1].split(',')[0]   # strip ',...'
                suffix = update_alts(cur_word)
                listbox.delete(index)
            elif insert_num:
                suffix = update_alts('')
                num_list.insert(index, num)
            else:
                suffix = update_alts('')
            listbox.insert(index, (num_str, u'%s %s' % (symb, word + suffix)))

        listbox.selection_clear(0, END)
        if   symb == '+' and self.temp.puz_defn:
            listbox.itemconfigure(index, fg=listbox_maingrid,
                                  selectforeground=listbox_maingrid)
        elif symb == '-' and word != null_word_symb:
            listbox.itemconfigure(index, fg=listbox_nogrid,
                                  selectforeground=listbox_nogrid)
        elif symb == '#':
            listbox.itemconfigure(index, fg=listbox_minigrid,
                                  selectforeground=listbox_minigrid)
        else:
            listbox.itemconfigure(index, fg='black', selectforeground='black')
        return index


# Listbox items are inserted after the word, clue portions are text-wrapped.
# Wrapped strings are saved in a cache to avoid repeated re-wrapping during
# undo/redo passes.

    def insert_with_caching(self, index, symb, num_str, word, clue,
                            listbox, cache):
        # used in clueful mode only
        string = u'%s %s %s %s' % (symb, word, clue_separator, clue)
        if index < len(cache):
            if string == cache[index][0]:
                listbox.insert(index, (num_str, cache[index][1]))
            else:
                wrapped = listbox.wrap_string(1, string)  # column 1 portion
                listbox.insert(index, (num_str, wrapped))
                cache[index] = (string, wrapped)
        else:
            wrapped = listbox.wrap_string(1, string)
            listbox.insert(index, (num_str, wrapped))
            # Assume indexes are in order when listbox is first populated;
            # once built the cache length should stay the same.
            cache.append((string, wrapped))


# ---------- Large-scale word entry ---------- #

# The following procedures are for wholesale entry and placement of all
# words in the current puzzle.

    def enter_words(self, perm):               # clueless mode
        show_alts = not perm.final
        for dir in (0,1):
            words   = perm.words[dir]
            grid_id = perm.grid_id[dir]
            for num in perm.nums[dir]:
                self.insert_num_word(dir, num, words[num], 0,
                                     grid_id.get(num), None, None, 0,
                                     show_alts=show_alts)

# The initial list of clues is entered in the listboxes with a white square
# used as placeholder for each word.

    def enter_clues(self, puz_defn):
        for dir in 0,1:
            nums = puz_defn.nums[dir]
            listbox = self.gui.wordbox[dir]
            cache = self.temp.wrapped_clues[dir]
            for index, num, clue in \
                    zip(range(len(nums)), nums, puz_defn.clues[dir]):
                    self.insert_with_caching(index, '-', str(num),
                                             null_word_symb,
                                             clue, listbox, cache)


    def enter_words_clues(self, perm):    # clueful mode, words and clues
        puz_defn = self.temp.puz_defn
        show_alts = not perm.final
        for dir in (0,1):
            words   = perm.words[dir]
            grid_id = perm.grid_id[dir]
            nums = puz_defn.nums[dir]
            listbox = self.gui.wordbox[dir]
            cache = self.temp.wrapped_clues[dir]
            for index, num, clue in \
                    zip(range(len(nums)), nums, puz_defn.clues[dir]):
                word = words.get(num)
                if word:
                    self.insert_num_word(dir, num, word, 0,
                                         grid_id.get(num), None, None, 0,
                                         show_alts=show_alts)
                else:
                    self.insert_with_caching(index, '-', str(num),
                                             null_word_symb,
                                             clue, listbox, cache)


    def reposition_words(self, preview, perm, new_posns,
                         new_id, show_alts=1):
        # Only those words in new_posns are (re)entered
        if preview: insert_op = self.insert_num_word_pre
        else:       insert_op = self.insert_num_word
        key_args = {'alts': None,    # don't create alternatives
                    'check': 1,
                    'show_alts': show_alts}
        for dir in (0,1):
            for n in perm.nums[dir]:
                cell = new_posns[new_id][dir].get(n)
                if cell:
                    insert_op(dir, n, perm.words[dir][n],
                              0, new_id, *cell, **key_args)

    def reposition_blocks(self, preview, new_keys, new_id):
        # Only those blocks in new_keys are (re)entered
        if preview: insert_op = self.place_block_pre
        else:       insert_op = self.place_block
        for row,col in new_keys[new_id].keys():
            insert_op(new_id, row, col, 0)


# ---------- Black square (block) management ---------- #

# Blacken or whiten non-lettered cells.  Dragging causes (nearly) all cells
# traversed to be blackened/whitened.

    def place_block_menu(self, toggle, id, row, col):
        def action(id, row, col):
            self.place_block_action(id, row, col, toggle)
        self.sess.next_click_action = action
        self.eph.block_toggle = toggle
        self.eph.multistep_mode = 1
        self.set_grid_cursors(None, 'dotbox')

# Start/finish block pasting.  On first call (before dragging),
# sess.preview = 1.

    def place_block_action(self, id, row, col, toggle):
        # start_action performed in calling environment
        if self.eph.preview:
            self.place_block(id, row, col, toggle)
            self.eph.drag_actions.append(
                lambda id,row,col: \
                    self.place_block(id, row, col, self.eph.block_toggle))
        else:
            self.save_action_string('Blacken/Whiten Square(s)')
            self.finish_action(None, id, key_move_aligned=1)
            self.restore_click_action()

# For blackening/whitening a single block, usually with accelerator key.

    def place_one_block(self, id=None, row=None, col=None):
        # start_action performed in calling environment
        if id == None:
            # invocation from keyboard accelerator
            location = self.find_grid_cell()[1:]  # look up mouse cursor posn
            if not location:
                return                            # ignore non-grid invocations
            id, row, col = location
            if self.sess.key_navigation:
                row, col = self.temp.key_cursors[id][1:3]
            self.start_action()                   # already done in popup case
        self.place_block(id, row, col)
        self.save_action_string('Blacken/Whiten Square(s)')
        self.finish_action(None, id, key_move_aligned=1)

# Argument 'toggle' has values: 0 - force cell black,
# 1 - toggle blackness, 2 - force cell white.
# For end blocks, don't add entry in perm.blocks[id] and when blackening
# an existing block, remove any perm entry.

    def place_block(self, id, row, col, toggle=1, end_block=0):
        size = grid_size[id]
        if not (0 <= row < size) or not (0 <= col < size):
            return       # ignore off-grid excursions
        key = (row, col)
        cells = self.aux.cells[id]
        cell= cells[row][col]
        if cell[0] or cell[1]:
            return       # ignore occupied cells
        elif (toggle == 2) or (toggle == 1) and cell[2]:
            if cell[2]:
                if row > 0 and cells[row-1][col][1] or \
                   col > 0 and cells[row][col-1][0] or \
                   row < size-1 and cells[row+1][col][1] or \
                   col < size-1 and cells[row][col+1][0]:
                    pass    # serving as end block -> leave intact
                else:
                    self.gui.grids[id].delete(cell[2])
                    cell[2] = None
                    try: del self.perm.blocks[id][key]
                    except KeyError: pass
        elif not cell[2]:
            cell[2] = self.paint_block(id, row, col, ('block',), block_color)
            if not end_block: self.perm.blocks[id][key] = 1
        else:   # blackening an already black square
            if end_block:  # end blocks overwrite any non-end blocks
                try: del self.perm.blocks[id][key]
                except KeyError: pass

    def place_block_pre(self, id, row, col, toggle=1):
        self.paint_block(id, row, col, ('preview',), block_pre_color)

    def place_blocks(self, perm):   # Place all blocks on grid (in force mode)
        for i in range(num_grids):
            for rc in perm.blocks[i].keys():
                self.place_block(i, rc[0], rc[1], 0)

# Paste a block (in force mode) at both ends of a word.  Also used to
# unpaste blocks.

    def append_blocks(self, dir, word_len, id, row, col, toggle=0):
        # force cell either black or white
        before = (row - dir, col - 1 + dir, toggle, 1)
        after  = (row + dir * word_len, col + (1-dir) * word_len, toggle, 1)
        if min(before) >= 0:            # cell good on top, left
            self.place_block(id, *before)
        if max(after) < grid_size[id]:  # cell good on bottom, right
            self.place_block(id, *after)

# Add all blocks implied by grid symmetry.  Each block within the
# current puzzle bounds is reflected according to the symmetry type.
# Tk objects for blocks are placed beneath other objects (lower in the
# stacking order) so there's no need to check for letters or blocks
# already in a cell.  Call only when symmetry is enabled.

    def add_symmetric_blocks(self):
        grid = self.gui.grids[0]       # only performed on main grid
        grid.delete('symm')            # be sure old ones are removed
        posns = self.perm.posns[0]
        words = self.perm.words
        blocks = []
        for dir in 0,1:
            for num, posn in posns[dir].items():
                r,c = posn
                blocks.append((r-dir, c-1+dir))
                wlen = len(words[dir][num])
                blocks.append((r + dir*wlen, c + (1-dir)*wlen))

        nc = self.temp.size_symm[3] - 1          # puzzle_width
        nr = self.temp.size_symm[4] - 1          # puzzle_height
        for r,c in blocks + self.perm.blocks[0].keys():
            if r <= nr and c <= nc:
                sr, sc = self.temp.symmetry_mapping(r, c, nr, nc)
                self.paint_block(0, sr, sc, ('symm',), sym_block_color, 1)



# ---------- Region movement operations ---------- #

# On a popup-initiated operation to move a region of the grid, the first
# step is to collect parameters and display a bounding box of the selected
# region.  The reference cell is also highlighted.  The event handler for
# left clicks is changed to catch the destination cell and complete the
# region movement.  A special mouse cursor is activated to show the mode.

    def start_region_translation(self, corner_x, corner_y, move_cursor,
                                 id_from, row_from, col_from):
        # start_action performed in calling environment
        corner_x *= grid_size[id_from] - 1
        corner_y *= grid_size[id_from] - 1
        corners = (min(corner_y, row_from), min(corner_x, col_from),
                   max(corner_y, row_from), max(corner_x, col_from))
        def within_region(row, col):
            return corners[0] <= row <= corners[2] and \
                   corners[1] <= col <= corners[3]
        def action(id, row, col):
            self.finish_region_translation(id, row, col, id_from,
                                           row_from, col_from, within_region)
        self.highlight_region_selection(id_from, within_region)
        paint_rect(self.gui.grids[id_from], *corners)
        self.sess.next_click_action = action
        self.eph.multistep_mode = 1
        self.set_grid_cursors(None, move_cursor)
        self.gui.status_line['text'] = \
            'Click and drag mouse cursor to move region to destination.'

# Highlight (color) words selected for region movement.  This allows
# a user to see the selection and abort before completing the motion.

    def highlight_region_selection(self, id, within_region, create_indic=1):
        posns = self.perm.posns[id]
        words = self.perm.words
        r_init, c_init = self.eph.init_posn
        drag_words = [[], []]
        head_cells = []
        ul_row, ul_col, lr_row, lr_col = 1000, 1000, 0, 0
        for dir in (0,1):
            for num, posn in posns[dir].items():
                row,col = posn
                if within_region(row, col):
                    word = words[dir][num]
                    self.paint_word_pre(id, dir, word, row, col,
                                        ('preview',), custom_red)
                    # Compute the upper left and lower right corners
                    # of the largest region extents.
                    ul_row = min(ul_row, row)
                    ul_col = min(ul_col, col)
                    if dir:
                        lr_row = max(lr_row, row+len(word))
                        lr_col = max(lr_col, col+1)
                    else:
                        lr_row = max(lr_row, row+1)
                        lr_col = max(lr_col, col+len(word))
                    head_cells.append(posn)
                    drag_words[dir].append((row - r_init, col - c_init,
                                            len(word)))

        # needed for display of indicator bars; corners are relative offsets
        self.eph.init_corners = (ul_row - r_init, ul_col - c_init,
                                 lr_row - r_init, lr_col - c_init)
        # Save selected head cells in case of error or cancellation;
        # user can retry to move these words if desired.
        self.temp.multiword_selection = [id, r_init, c_init, head_cells,
                                         self.eph.init_corners]

        # Descriptors for words to be moved are saved.  Each contains
        # the relative row and column and the word length.
        self.eph.drag_words = drag_words
        self.eph.drag_actions.append(self.check_dragging_words)

        if create_indic:
            self.eph.start_preview_actions.append(
                lambda id_to: self.gui.create_indicators[id_to](2))

    def highlight_previous_selection(self, id):
        id, r_init, c_init, head_cells, corners = self.temp.multiword_selection
        posns = self.perm.posns[id]
        words = self.perm.words
        for dir in (0,1):
            for num, posn in posns[dir].items():
                if posn in head_cells:
                    word = words[dir][num]
                    self.paint_word_pre(id, dir, word, posn[0], posn[1],
                                        ('preview',), custom_red)
        self.eph.drag_actions.append(self.check_dragging_words)
        self.eph.start_preview_actions.append(
            lambda id_to: self.gui.create_indicators[id_to](2))

# Check for overlaps between end blocks of moving words and letters of
# stationary words, and vice versa.  Draw a red box around clashing cells,
# so user can see when an invalid configuration would result.

    def check_dragging_words(self, id, row, col):
        cells = self.aux.cells[id]
        grid  = self.gui.grids[id]
        size  = grid_size[id]
        for dir in 0,1:
            for r1, c1, w_len in self.eph.drag_words[dir]:
                r, c = row + r1, col + c1
                # check moving blocks against stationary letters
                for rb, cb in ((r-dir, c-1+dir),
                               (r+w_len*dir, c+w_len*(1-dir))):
                    if rb < 0 or cb < 0 or rb >= size or cb >= size:
                        continue
                    if cells[rb][cb][0] or cells[rb][cb][1]:
                        paint_cell_border(grid, rb, cb)
                # check moving letters against stationary blocks
                for k in range(w_len):
                    if r >= size or c >= size: break
                    if r >= 0 and c >= 0 and cells[r][c][2]:
                        paint_cell_border(grid, r, c)
                    r += dir; c += 1-dir

# The actual movement takes place here.  Row and column deltas are computed.
# Any word whose position (first letter) satisfies the predicate
# within_region will be shifted by the deltas.  Black squares are moved
# as well.  A check is made for each shift to ensure no grid overflow or
# word placement conflict occurs.
# Any errors cause the state to be restored.

    def finish_region_translation(self, id_to, row_to, col_to,
                                  id_from, row_from, col_from, within_region):
        preview = self.eph.preview
        limit = grid_size[id_to] - 1
        row_to = max(0, min(row_to, limit))    # clamp in case row, col
        col_to = max(0, min(col_to, limit))    # go out of bounds
        delta_row = row_to - row_from
        delta_col = col_to - col_from

        new_posns, new_keys = [],[]          # collect for later rebuild
        for i in range(num_grids):
            new_posns.append([{},{}])
            new_keys.append({})
        if preview:
#            self.gui.create_indicators[id_to](2, self.eph.init_posn)
            self.eph.old_posns = old_posns = copy.deepcopy(self.perm.posns)
            self.eph.old_keys  = old_keys  = copy.deepcopy(self.perm.blocks)
            self.eph.old_kc_posn = None
            # Delete blocks on preview pass
            for row, col in old_keys[id_from].keys():
                if within_region(row, col):
                    self.place_block(id_from, row, col, 2)  # erase block
        else:
            self.gui.destroy_indicators[id_to]()
            old_posns = self.eph.old_posns  # preview occurred if != None
            old_keys  = self.eph.old_keys
            self.eph.old_posns = None
            self.eph.old_keys  = None
        for row, col in old_keys[id_from].keys():
            if within_region(row, col):
                new_keys[id_to][(row+delta_row, col+delta_col)] = 1
        word_posns = old_posns or self.perm.posns
        del_words = preview or not old_posns  # can't delete words twice

        # if key cursor lies on a moved word, move cursor too
        if preview and self.sess.key_navigation and id_from == id_to:
            krow, kcol = self.temp.key_cursors[id_from][1:3]
            kcell = self.aux.cells[id_from][krow][kcol]
            for d in 0,1:
                if kcell[d]:
                    khead = word_posns[id_from][d][kcell[d][0]]
                    if within_region(*khead):
                        self.eph.old_kc_posn = krow, kcol

        # move words by translating by deltas; delete old words when present
        head_cells = []
        for dir in (0,1):
            for num, posn in word_posns[id_from][dir].items():
                row, col = posn
                if within_region(row, col):
                    if del_words: self.del_word_grid(id_from, dir, row, col)
                    head = (row+delta_row, col+delta_col)
                    new_posns[id_to][dir][num] = head
                    head_cells.append(head)
        try:
            self.reposition_words(preview, self.perm, new_posns, id_to)
            self.reposition_blocks(preview, new_keys, id_to)
            if not preview:
                if self.eph.old_kc_posn:
                    krow, kcol = self.eph.old_kc_posn
                    self.set_key_cursor(adjust=0,
                                        posn=(krow+delta_row, kcol+delta_col))
                moved = (len(new_posns[id_to][0]), len(new_posns[id_to][1]))
                self.save_action_string('Move %s Words' % (moved[0]+moved[1]))
                self.finish_action(None, id_from)
                self.close_action(id_to)
                self.restore_click_action()
                self.gui.status_line['text'] = \
                    '%s across words and %s down words were moved.' % moved
                # save selection for redo purposes;
                # make sure this assignment follows finish_action
                self.temp.multiword_selection[0] =  id_to
                self.temp.multiword_selection[1] += delta_row
                self.temp.multiword_selection[2] += delta_col
                self.temp.multiword_selection[3] =  head_cells
        except UserError:
            if user_dialog(askokcancel,
                           *dialog_messages['try_another_destination']):
                # trying again: undo effects of unfinished command and
                # make a fresh copy of recovery_state
                self.restore_state_partial()
                self.temp.recovery_state = copy.deepcopy(self.perm)
                self.close_action_partial(id_to)
                # need to avoid extra copies of actions:
                self.eph.start_preview_actions = []
                self.redo_word_translation(id_from, row_from, col_from)
            else:
                self.restore_state(id_from)
                self.close_action(id_to)
                self.restore_click_action()


# If a previous multiword translation was performed recently,
# move the previously selected words to a new location.
# If a valid prior movement is active, temp.multiword_selection
# will contain (grid id, head cell list).

    def redo_word_translation(self, id_from, row_from, col_from):
        if not self.temp.multiword_selection:
            user_dialog(showerror, *error_messages['no_multiword_redo'])
            self.close_action(id_from)
            self.restore_click_action()
            raise FalseStart
        id_prev, irow, icol, head_cells, corners = self.temp.multiword_selection

        def within_region(row, col):
            return (row, col) in head_cells
        def action(id, row, col):
            self.finish_region_translation(id, row, col, id_prev,
                                           irow, icol, within_region)
        self.highlight_previous_selection(id_from)
        self.eph.init_corners = corners
        self.eph.init_posn = (-1, -1)    # force click_1 to set posn
        self.sess.next_click_action = action
        self.eph.multistep_mode = 1
        self.set_grid_cursors(None, 'fleur')
        self.gui.status_line['text'] = \
            'Click and drag mouse cursor to move words to a new destination.'


# Moving a single word is treated as a special case of the following
# region-movement operations.  If word is a double head cell, will move
# both words.

    def start_single_word_translation(self, id_from, row_from, col_from,
                                      head_row_col=None):
        # row_from, col_from represent the point of origin;
        # word_row, word_col is the head cell
        if head_row_col:
            word_row, word_col = head_row_col
        else:
            word_row, word_col = row_from, col_from

        def within_region(row, col):
            return row == word_row and col == word_col
        def action(id, row, col):
            self.finish_region_translation(id, row, col, id_from,
                                           row_from, col_from, within_region)
        self.highlight_region_selection(id_from, within_region)
        self.sess.next_click_action = action
        self.eph.multistep_mode = 1
        self.set_grid_cursors(None, 'fleur')
        self.gui.status_line['text'] = \
            'Click and drag mouse cursor to move the word.'

    def start_single_word_trans_action(self, dir, id_from, row_from, col_from):
        cell = self.aux.cells[id_from][row_from][col_from][dir]
        if cell and cell[0]:
            self.start_single_word_translation(
                id_from, row_from, col_from,
                self.perm.posns[id_from][dir][cell[0]])
        else:
            # this case has nothing to move; maybe should give error ###
            self.start_single_word_translation(id_from, row_from, col_from)


# Moving all the words on a grid requires the same click sequence as
# moving a rectangular region.  The upper left corner of the bounding
# box is used as the reference point.  The rest of the processing
# proceeds the same as with rectangular region movement.

    def start_all_words_translation(self, id_from, row_from, col_from):
        grid  = self.gui.grids[id_from]
        posns = self.perm.posns[id_from]
        grid_posns = posns[0].values() + posns[1].values()
        def within_region(row, col):  return 1
        def action(id, row, col):
            self.finish_region_translation(id, row, col, id_from,
                                           row_from, col_from, within_region)
        self.highlight_region_selection(id_from, within_region)
        self.sess.next_click_action = action
        self.eph.multistep_mode = 1
        self.set_grid_cursors(None, 'fleur')
        self.gui.status_line['text'] = \
            'Click and drag mouse cursor to move region to destination.'

# Moving all the connected words from a given cell requires
# the same click sequence as moving a rectangular region.
# First all the connected words are identified by examining the
# cells from the first word(s) and propagating the search to all
# crossing words.  A full closure of the words connected to the
# orginal cell is performed.  The rest of the processing
# proceeds the same as with rectangular region movement.

    def start_adjacent_words_translation(self, id_from, row_from, col_from,
                                         connected=0):
        # check for empty cell??
        grid  = self.gui.grids[id_from]
        cells = self.aux.cells[id_from]
        posns = self.perm.posns[id_from]
        words = self.perm.words
        limit = grid_size[id_from]
        visited    = [{}, {}]       # word numbers
        head_cells = {}

        def visit_cell(dir, row, col):
            start_cell = cells[row][col]
            if not start_cell[dir]: return

            num = start_cell[dir][0]
            head = posns[dir][num]
            head_cells[head] = 1
            visited[dir][num] = 1
            wlen = len(words[dir][num])

            # first scan current word and visit each crossing word
            for r,c in generate_cells(dir, wlen, *head):
                cell = cells[r][c][1-dir]
                if cell and not visited[1-dir].has_key(cell[0]):
                    visit_cell(1-dir, r, c)
            if connected: return

            h_row, h_col = head
            # if not at top/left row/col, check cells of previous word
            prev = (h_row, h_col - 1) if dir else (h_row - 1, h_col)
            if prev[0] >= 0 and prev[1] >= 0:
                for r,c in generate_cells(dir, wlen, *prev):
                    cell = cells[r][c][dir]
                    if cell and not visited[dir].has_key(cell[0]):
                        visit_cell(dir, r, c)
            # if not at bottom/right row/col, check cells of next word
            next = (h_row, h_col + 1) if dir else (h_row + 1, h_col)
            if next[0] < limit and next[1] < limit:
                for r,c in generate_cells(dir, wlen, *next):
                    cell = cells[r][c][dir]
                    if cell and not visited[dir].has_key(cell[0]):
                        visit_cell(dir, r, c)

        visit_cell(0, row_from, col_from)
        if cells[row_from][col_from][0] == None:
            visit_cell(1, row_from, col_from)

        def within_region(row, col):
            return (row, col) in head_cells
        def action(id, row, col):
            self.finish_region_translation(id, row, col, id_from,
                                           row_from, col_from, within_region)
        self.highlight_region_selection(id_from, within_region)
        self.sess.next_click_action = action
        self.eph.multistep_mode = 1
        self.set_grid_cursors(None, 'fleur')
        self.gui.status_line['text'] = \
            'Click and drag mouse cursor to move %s %s words.' \
            % (len(visited[0]) + len(visited[1]),
               ('adjacent', 'connected')[connected])

    def start_connected_words_translation(self, id_from, row_from, col_from):
        self.start_adjacent_words_translation(id_from, row_from, col_from, 1)


# A region may be defined using a three-segment boundary containing a
# diagonal and two risers.  This requires three clicks: the popup cell
# gives one diagonal endpoint, a second click gives the other, and a
# third click gives the target cell for moving the region.  Click-3
# defines which side of the boundary gets moved.  Deltas are computed
# from click-3 - click-2.  Lines are displayed to show the boundary,
# which is adjusted when click-2 is dragged.  The reference cell (click-1)
# is also highlighted.  The event handler for left clicks is changed to
# catch the click-2 and click-3 cells and complete the region movement.
# Special mouse cursors are activated to show the mode.

    def start_diagonal_region(self, move_right, id_from, row_from, col_from):
        def action(id, row, col):
            self.continue_diagonal_region(id, row, col,
                                          id_from, row_from, col_from,
                                          move_right)
        self.sess.next_click_action = action
        self.eph.multistep_mode = 1
        self.set_grid_cursors(None, 'fleur')
        self.gui.status_line['text'] = \
            'Click on second cell to define diagonal boundary.'

    def continue_diagonal_region(self, id, row_endpt, col_endpt,
                                 id_from, row_from, col_from, move_right):
        if id != id_from:
            user_dialog(showerror, *error_messages['diagonal_id_mismatch'])
            self.close_action(id_from, id)
            self.restore_click_action()
            raise FalseStart

        # collect upper (p_r, p_c) and lower (q_r, q_c) row, col
        p_r, p_c, q_r, q_c = \
            self.plot_diagonal_boundary(id, row_endpt, col_endpt,
                                        row_from, col_from)
        if self.eph.preview:
            self.eph.drag_actions.append(
                lambda id,row,col: \
                    self.plot_diagonal_boundary(id, row, col,
                                                row_from, col_from))
        else:
            if p_c != q_c:
                slope = float(q_r - p_r) / (q_c - p_c)
            def in_right_region(row, col):
                if p_c == q_c:    # vertical line
                    return col >= p_c
                if (row <= p_r and col >= p_c) or (row >= q_r and col >= q_c):
                    return 1
                if slope > 0.0:
                    return col >= p_c and row <= slope * (col - p_c) + p_r
                else:
                    return col >= q_c and row >= slope * (col - p_c) + p_r
            def within_region(row, col, move_right=move_right):
                outcome = in_right_region(row, col)
                return outcome if move_right else not outcome
            def action(id, row, col):
                self.finish_diagonal_region(id, row, col,
                                            id_from, row_endpt, col_endpt,
                                            in_right_region, within_region)
            self.eph.init_posn = (row_endpt, col_endpt)
            self.highlight_region_selection(id_from, within_region,
                                            create_indic=0)
            # repaint boundary to raise it above cell highlighting
            self.plot_diagonal_boundary(id, row_endpt, col_endpt,
                                        row_from, col_from)
            self.sess.next_click_action = action
#            self.eph.drag_actions = []    ### highlight... adds new actions
            self.eph.multistep_mode = 2
            self.gui.status_line['text'] = \
                'Click on destination cell to move region.'

    def plot_diagonal_boundary(self, id, row_endpt, col_endpt,
                               row_from, col_from):
        if row_from <= row_endpt:
            p_r, p_c = row_from, col_from
            q_r, q_c = row_endpt, col_endpt
        else:
            p_r, p_c = row_endpt, col_endpt
            q_r, q_c = row_from, col_from
        self.gui.grids[id].delete('aids')      # erase prior boundary
        paint_diagonal_boundary(self.gui.grids[id], p_r, p_c, q_r, q_c,
                                grid_size[id])
        return p_r, p_c, q_r, q_c

    def finish_diagonal_region(self, id, row, col,
                               id_from, row_from, col_from,
                               in_right_region, within_region):
        # final (up) event should go directly to finish_region_translation
        if not self.eph.preview: return
        self.gui.grids[id_from].delete('aids')      # erase prior boundary
        def action(id, row, col):
            self.finish_region_translation(id, row, col,
                                           id_from, row_from, col_from,
                                           within_region)
        self.eph.init_posn = (row, col)
        self.gui.create_indicators[id](2)
        self.sess.next_click_action = action   # for button-up event later
        action(id, row, col)                   # do preview action now


# The 'wrap' feature is implemented as in region translation.  The cleavage
# column is used to create two portions split vertically.  Any words/blocks
# on the right are shifted to the left and down one row.  The shift amount
# is computed by detecting the last nonempty column.  The left side is
# shifted right by the same amount to make room.

    def wrap_grid_horiz(self, id, row_dummy, edge):
        # start_action performed in calling environment
        self.master.update_idletasks()    # show aids before taking action
        keys = self.perm.blocks[id].keys()
        for row,col in keys:
            self.place_block(id, row, col, 2)     # erase current blocks first
        last = edge
        size = grid_size[id]
        cells = self.aux.cells[id]
        for col in range(edge+1, size):   # find last nonnull column
            for row in range(size):
                if cells[row][col] != null_cell:
                    last = col
                    break
        delta = last - edge + 1
        new_posns = []             # collect for later rebuild
        for i in range(num_grids): new_posns.append([{},{}])
        for dir in (0,1):
            for num, posn in self.perm.posns[id][dir].items():
                row,col = posn
                self.del_word_grid(id, dir, row, col)
                if edge <= col:
                    new_posns[id][dir][num] = (row+1, col-edge)
                else:
                    new_posns[id][dir][num] = (row, col+delta)
        try:
            self.reposition_words(0, self.perm, new_posns, id)
            for row,col in keys:    # use 2 passes to avoid clashes
                if edge <= col:
                    self.place_block(id, row+1, col-edge, 0)
                else:
                    self.place_block(id, row, col+delta, 0)
            self.gui.status_line['text'] = \
                'Words were wrapped around column %s.' % (edge+1)
            self.save_action_string('Wrap Words')
            self.finish_action(None, id)
        except UserError:
            self.restore_state(id)


# ---------- Puzzle finalization ---------- #

# A puzzle is finalized by finding its bounding box, erasing any blocks
# outside of this box, moving the puzzle to the upper left corner, then
# blackening any empty squares.  An attribute is set in perm to indicate
# the finalization state.  Afterward, no changes may be made to the
# puzzle state.  Consequently, it suffices to change only Tk objects.
# Assumes only grid 0 needs to be processed.

    def finalize_puzzle(self, prev_final=(), check=1):
        if self.perm.final: return
        if self.perm.nums == [[], []]: return
        size = grid_size[0]
        cells = self.aux.cells[0]
        grid = self.gui.grids[0]
        def edge_row(start, stop, delta):
            # find row at puzzle's edge (contains letters)
            for row in range(start, stop, delta):
                for col in range(size):
                    if cells[row][col][0] or cells[row][col][1]: return row
            return stop
        def edge_col(start, stop, delta):
            # find column at puzzle's edge (contains letters)
            for col in range(start, stop, delta):
                for row in range(size):
                    if cells[row][col][0] or cells[row][col][1]: return col
            return stop
        top_row, bottom_row = edge_row(0, size, 1), edge_row(size-1, -1, -1)
        left_col, right_col = edge_col(0, size, 1), edge_col(size-1, -1, -1)
        soln_checked = 0
        if check:
            self.check_if_finalizeable()                   ### excep
            if self.temp.puz_defn and self.temp.puz_defn.soln_words:
                if self.temp.puz_defn.soln_flags:
                    if not user_dialog(askokcancel,
                                       *dialog_messages['confirm_unchecked']):
                        # solution locked; user wants to unlock it first
                        raise FalseStart
                    # else: user finalizing without checking
                elif self.check_solution(1, top_row, left_col):
                    soln_checked = 1
                else:
                    raise FalseStart
        self.stop_timer()

        if not prev_final:
            # after finding extent of rows, columns having letters, delete all
            # blocks, then move everything to the upper left corner
            cur_blocks = copy.deepcopy(self.perm.blocks[0])
            for row,col in cur_blocks.keys():
                self.place_block(0, row, col, 2)        # force blocks white
            new_posns = [[{},{}]]
            # move words by translating by deltas; delete current words first
            for dir in (0,1):
                for num, (row,col) in self.perm.posns[0][dir].items():
                    self.del_word_grid(0, dir, row, col)
                    new_posns[0][dir][num] = (row - top_row, col - left_col)
            self.reposition_words(0, self.perm, new_posns, 0, show_alts=0)

        # now blacken all empty cells
        for row in range(bottom_row - top_row + 1):
            for col in range(right_col - left_col + 1):
                if cells[row][col] == null_cell:
                    self.paint_block(0, row, col, ('block',), block_color)
        # save deltas, current blocks for restoration on undo
        self.perm.final = prev_final or (top_row, left_col, cur_blocks)
        # cover up grid lines outside of bounding box
        y0 = (bottom_row - top_row + 1) * cell_size + 1
        x0 = (right_col - left_col + 1) * cell_size + 1
        limit = size * cell_size + 1
        grid.create_polygon(0, y0, x0, y0, x0, 0,
                            limit, 0, limit, limit, 0, limit,
                            outline='', fill=outer_bg_color, tags=('final',))
        grid.delete('symm')           # be sure symmetry blocks are removed
        grid.delete('key_cursor')    # be sure key cursor is removed
        grid.delete('infer2')         # and its inferred number
        grid.delete('infer')
        self.gui.destroy_indicators[0]()
        self.perform_followup_actions()
        self.set_grid_cursors(2)
        self.gui.status_line['text'] = \
            'Completed puzzle has been finalized (frozen).  ' \
            'Undo to re-enable editing.'
        self.gui.status_line2['text'] = ''
        self.eph.solve_time_id = \
            update_msg_widget(self.gui.solving_time,
                              self.gui.solving_time['text'],
                              self.eph.solve_time_id,
                              fg_color=msg_saved_color)

        if not (self.temp.undo_state and \
                    self.temp.undo_state[-1][2].startswith('Finalize')):
            self.temp.undo_state.append((self.perm,
                                         self.nonperm_recovery_state(),
                                         'Finalize Puzzle'))
        for after_id in (self.eph.scroll_id, self.eph.visit_id):
            grid.after_cancel(after_id)
        for d in 0,1: self.gui.wordbox[d].yview_moveto(0)
        if soln_checked:
            msgs = ['Congratulations! Your solution is correct.']
            self.eph.temp_msg_id = \
                show_temp_msg_panel(msgs, self.eph.temp_msg_id,
                                    self.gui.temp_msg_panel, 30, 20)
        # self.finish_action()    # omit for now
        self.update_word_counts()

# A variety of checks is performed before allowing finalization.  If any
# check fails, the user gets an error message so he can adjust the puzzle
# and retry later.

    def check_if_finalizeable(self):         # raises FalseStart
        def gen_word_list_text(lists, msg):
            if lists[0] and lists[1]: and_text = ' and'
            else:                     and_text = ''
            wtext = ['', '']
            for dir in (0,1):
                if lists[dir]:
                    wtext[dir] = ' %s %s' % (lists[dir], dir_text[dir])
            return 'Words%s%s%s %s' % (wtext[0], and_text, wtext[1], msg)
        
        # minigrids must be empty
        posns = self.perm.posns
        nums  = self.perm.nums
        ids   = self.perm.grid_id
        for i in range(1, num_grids):
            if posns[i] != [{},{}] or self.perm.blocks[i] != {}:
                user_dialog(showerror, *error_messages['final_while_mini'])
                raise FalseStart

        # in clueful mode, each clue must have a word
        if self.temp.puz_defn:
            collect = ([], [])
            for dir in (0,1):
                clue_nums = self.temp.puz_defn.nums[dir]
                for num in clue_nums:
                    if num not in nums[dir]:
                        collect[dir].append(num)    # no word for this clue
            if collect[0] or collect[1]:
                user_dialog(showerror, 'Finalize puzzle',
                            gen_word_list_text(
                                collect, 'have not yet been entered.'))
                raise FalseStart

        # all known words must appear on the main grid
        collect = ([], [])
        for dir in (0,1):
            for num in nums[dir]:
                if not ids[dir].has_key(num): collect[dir].append(num)
        if collect[0] or collect[1]:
            user_dialog(showerror, 'Finalize puzzle',
                        gen_word_list_text(
                            collect, 'have not yet been pasted on the grid.'))
            raise FalseStart
        
        # scan the cells of all words and check for underspecification
        # (placeholders still in place) and overspecification (letter clashes)
        collect = ([], [], [], [])
        words = self.perm.words
        cells = self.aux.cells[0]
        for dir in (0,1):
            for num in nums[dir]:
                for r,c in generate_cells(dir, len(words[dir][num]),
                                          *posns[0][dir][num]):
                    cell = cells[r][c]
                    if cell[dir] and cell[dir][2] == placeholder:
                        if not cell[1-dir] or cell[1-dir][2] == placeholder:
                            collect[dir].append(num)
                            break
                    if cell[dir] and cell[1-dir] and \
                       cell[dir][2]   != placeholder and \
                       cell[1-dir][2] != placeholder and \
                       cell[dir][2] != cell[1-dir][2]:
                        collect[2+dir].append(num)
                        break
        if collect[0] or collect[1]:
            user_dialog(showerror, 'Finalize puzzle',
                        gen_word_list_text(collect[:2],
                            'still contain placeholder characters.'))
            raise FalseStart
        if collect[2] or collect[3]:
            user_dialog(showerror, 'Finalize puzzle',
                        gen_word_list_text(collect[2:],
                                           'contain letter clashes.'))
            raise FalseStart

        # scan the cells of all words and check that for each letter that has
        # no letter above or to its left, that a word begins at that cell
        collect = ([], [])
        for dir in (0,1):
            for num in nums[dir]:
                r, c = posns[0][dir][num]
                wlen = len(words[dir][num])
                if r*(1-dir) + c*dir == 0 :
                    # handle case of top row or leftmost column
                    for k in range(wlen):
                        if not cells[r][c][1-dir] :
                            collect[1-dir].append((r, c))
                        r += dir; c += 1-dir
                    continue
                for k in range(wlen):
                    # scan word along row or column
                    prev = cells[r-(1-dir)][c-dir]    # above or to the left
                    # prev[1-dir] -> part of crossing word;
                    # prev[dir] -> not in word, but already counted
                    if not prev[dir] and not prev[1-dir] and \
                       not cells[r][c][1-dir] :
                        collect[1-dir].append((r, c))
                    r += dir; c += 1-dir
            for r,c in collect[1-dir]:
                paint_missing_head(self.gui.grids[0], 1-dir, r, c)
        if collect[0] or collect[1]:
            if app_prefs['infer_nums'] and not self.temp.puz_defn and \
                    user_dialog(askokcancel,
                                *dialog_messages['confirm_complete_words']):
                for dir in (0,1):
                    for r,c in collect[dir]:
                        word = self.infer_letters_cross(dir, 0, r, c)
                        self.insert_auto_completion(dir, 1, word, 0, r, c)
                self.gui.grids[0].delete('error')   # remove highlighting
                return
        if collect[0] or collect[1]:
            if user_dialog(askokcancel,
                           *dialog_messages['confirm_missing_finalize']):
                # user overriding finalization check
                self.gui.grids[0].delete('error')   # remove highlighting
            else:
                raise FalseStart

# Restore words and blocks to the original positions they had before
# finalization.  Move words by translation; delete current words first.
# Main grid only.

    def restore_original_posns(self, top_row, left_col, blocks):
        if top_row == left_col == 0: return
        new_posns = [[{},{}]]
        for dir in (0,1):
            for num, (row,col) in self.perm.posns[0][dir].items():
                self.del_word_grid(0, dir, row, col)
                new_posns[0][dir][num] = (row + top_row, col + left_col)
        self.reposition_words(0, self.perm, new_posns, 0)
        for row,col in blocks.keys():
            self.place_block(0, row, col, 0)     # force blocks black


# When all solution-designated cells are filled with letters, check that
# that they match the solution grid.  Some words might not yet be entered,
# but their letters must be filled in by crossing words.  Also check that
# no additional letters are present.  If everything matches, we consider
# the puzzle solved and complete the missing words for the user, thereby
# performing an implicit finalization.

    def check_cell_letters(self):
        puz_defn = self.temp.puz_defn
        if puz_defn.soln_flags:
            return    # solution locked; let user finalize explicitly
        cells = self.aux.cells[0]
        width, height = puz_defn.width, puz_defn.height
        soln_grid = puz_defn.soln_grid

        for row in range(height):
            cell_row = cells[row]
            soln_row = soln_grid[row].upper()
            for col in range(width):
                cell = cell_row[col]
                a_letter = cell[0] and cell[0][2].upper()
                d_letter = cell[1] and cell[1][2].upper()
                if a_letter and a_letter != soln_row[col] or \
                   d_letter and d_letter != soln_row[col] :
                    return False

        # All checks pass so let's complete the puzzle.
        if app_prefs['upper_case']: trans = lambda s: s.upper()
        else:                       trans = lambda s: s.lower()
        for dir in (0,1):
            posns = self.perm.posns[0][dir]
            soln_words = puz_defn.soln_words[dir]
            soln_posns = puz_defn.soln_posns[dir]
            for num in soln_words:
                if num not in posns or posns[num] != soln_posns[num]:
                    row, col = soln_posns[num]
                    word = trans(soln_words[num])
                    self.insert_num_word(dir, num, word,
                                         0, 0, row, col, check=0)
        return True


# ---------- Setting puzzle parameters ---------- #

# A puzzle's bounding box can be declared by the user.  The background
# color for the out-of-bounds region is changed, but the cells can
# still be used.  Can be invoked repeatedly; previous background is
# deleted first.  Assumes only grid 0 needs to be processed.  Action on
#   use_session = 0 : read and write self.temp.size_symm
#   use_session = 1 : read and write self.sess values
#   use_session = 2 : read sess values, write to both temp and sess

    def set_puzzle_size(self, use_session=1, *args):
        if args:
            use_size, apply_symm, symm_type, raw_width, raw_height = args
        elif use_session:
            use_size   = self.sess.show_boundary
            apply_symm = self.sess.apply_symmetry
            symm_type  = self.sess.symmetry_type
            raw_width  = self.sess.puzzle_width
            raw_height = self.sess.puzzle_height
        else:
            use_size, apply_symm, symm_type, raw_width, raw_height = \
                self.temp.size_symm

        # puz file asymmetric => override apply_symm
        apply_symm = symm_type and apply_symm
        if not (use_size and apply_symm):
            if use_session != 1:
                self.gui.grids[0].delete('symm')   # remove symmetry blocks
                # self.temp.size_symm will be updated later
            if use_session:
                self.sess.apply_symmetry = 0
        if not use_size:
            if use_session == 1:
                self.eph.warnings['size_symm_session'] = 1
            else:
                self.gui.grids[0].delete('outer')  # remove previous background
                self.temp.size_symm = (0, 0, 'rot', 0, 0)
            if use_session:
                self.sess.show_boundary = 0
            self.perform_followup_actions()
            self.gui.status_line['text'] = \
                'Size and symmetry attributes have been applied.'
            return

        size = grid_size[0]
        width  = validate_puzzle_size(raw_width, size)
        height = validate_puzzle_size(raw_height, size)
        if symm_type in ('ul-lr', 'ur-ll') and width != height:
            user_dialog(showerror, *error_messages['size_not_square'])
            raise FalseStart

        if use_session:
            self.sess.show_boundary  = 1
            self.sess.apply_symmetry = apply_symm
            self.sess.symmetry_type  = symm_type
            self.sess.puzzle_width   = width
            self.sess.puzzle_height  = height
        if apply_symm:
            self.temp.symmetry_mapping = symmetry_mappings[symm_type]

        if use_session == 1:
            self.eph.warnings['size_symm_session'] = 1
            self.perform_followup_actions()
            self.gui.status_line['text'] = \
                'Puzzle bounds have been established for this session.'
            return
        elif self.temp.puz_defn:
            if self.temp.puz_defn.format_type == 'scanned':
                # in semi-clueful mode can override initial settings
                self.temp.puz_defn.width  = width
                self.temp.puz_defn.height = height
                self.temp.puz_defn.symmetry_type = symm_type
                self.temp.size_symm = \
                    (use_size, apply_symm, symm_type, width, height)
            else:
                # in clueful mode size is fixed, type can be overridden
                t_wd, t_ht = self.temp.size_symm[3:5]
                self.temp.size_symm = \
                    (use_size, apply_symm, symm_type, t_wd, t_ht)
                if t_wd != width or t_ht != height:
                    self.eph.warnings['size_cant_change'] = 1
        else:
            self.temp.size_symm = \
                (use_size, apply_symm, symm_type, width, height)
                    
        grid = self.gui.grids[0]
        top_row, bottom_row = 0, height - 1
        left_col, right_col = 0, width - 1

        # insert different background color for out-of-bounds region
        y0 = (bottom_row - top_row + 1) * cell_size + 1
        x0 = (right_col - left_col + 1) * cell_size + 1
        limit = size * cell_size + 1
        grid.delete('outer')   # remove previous background
        region = grid.create_polygon(0, y0, x0, y0, x0, 0,
                                     limit, 0, limit, limit, 0, limit,
                                     outline='', fill=outer_bg_color,
                                     tags=('outer',))
        grid.tag_lower(region, 1)  # place it below all other items
        self.perform_followup_actions()
        self.gui.status_line['text'] = \
            'Puzzle bounds have been established.'
        # self.finish_action()    # omit for now
        

# ---------- Grid display methods ---------- #

# Paint a block with assigned tags and color.

    def paint_block(self, id, row, col, tags, color, lower=0):
        x_0 = col * cell_size
        y_0 = row * cell_size
        rect = self.gui.grids[id].create_rectangle(
                   x_0, y_0, x_0 + cell_size, y_0 + cell_size,
                   fill=color, outline=color, tags=tags)
        if lower:  # some blocks are placed below other items
            self.gui.grids[id].tag_lower(rect, lower)
        return rect
            
# Word is upcased, placed in grid and displayed on the canvas.  Canvas tags
# include 'letter' (for convenient deletion of all cells) and word-specific
# tags, e.g., 'a7' or 'd7'.  For each letter of the new word, it is checked
# against any current cell contents.  If a clash is detected, a marker is
# requested for the displayed cell.  If a placeholder appears in either
# the current word or a crossing word, the placeholder acquires the
# other letter.  Return word with updated (acquired) letters.

    def paint_word(self, id, dir, num, word, row, col):
        grid = self.gui.grids[id]
        tag = '%s%d' % (('a','d')[dir], num)
        cells = self.aux.cells[id]
        posns = self.perm.posns[id]
        letters = list(word)         # expand string to allow substitutions
        r,c = row,col
        for i in range(len(letters)):
            cross_cell = cells[r][c][1-dir]  # cell of crossing word
            clash, clash_num = 0, 0
            paint_text = letters[i]
            if cross_cell:
                if letters[i] == placeholder:
                    paint_text = letters[i] = cross_cell[2]
                elif cross_cell[2] == placeholder:
                    # change crossing letter to new letter;
                    # schedule for later to avoid inconsistent states
                    index = self.letter_index(1-dir, id, r, c)
                    self.eph.followup_actions.append(
                        (index, self.update_gridded_letter,
                         (1-dir, cross_cell[0], id, letters[i],
                          index, letters[i])))
                else:
                    clash = letters[i] != cross_cell[2]
                    if clash:
                        if dir: paint_text = cross_cell[2], letters[i]
                        else:   paint_text = letters[i], cross_cell[2]
                        grid.delete(letter_cell_tag(cross_cell[1], r, c))
                        if i > 0:
                            index = self.letter_index(1-dir, id, r, c)
                            if index == 0:                 # head cell: need to
                                clash_num = cross_cell[0]  # redraw its number
            # do following assignment after cross-cell processing because
            # letters[i] might get updated
            if cells[r][c][dir] == None:
                cells[r][c][dir] = (num, tag, letters[i])
            if letters[i] == placeholder: color = placeholder_color
            else:                         color = 'black'
            paint_cell(grid, r, c, paint_text, tag,
                       (i==0) and num or clash_num, clash, color)
            r += dir; c += 1-dir
        posns[dir][num] = (row, col)
        self.perm.grid_id[dir][num] = id
        new_word = ''.join(letters)    # return to string form
        return new_word

# Words can be temporarily painted for preview, error uses.
# Offset is number of rows/cols below/over to place text;
# pointer indicates display of triangle pointer.

    def paint_word_temp(self, id, dir, word, tail, row, col,
                        tags, offset=0, pointer=0):
        if not word: return
        grid = self.gui.grids[id]
        size = grid_size[id]
        cells = self.aux.cells[id]
        word_len = len(word)
        # drop letters that fall off end of grid
        wlen = min(word_len, size - row*dir - col*(1-dir))
        # offset by one row/col if requested
        r, c = row + (1-dir) * offset, col + dir * offset  # use min?
        dr, dc = -(1-dir) * offset, -dir * offset

        # first cell is handled separately so key cursor can show below
        if self.sess.key_navigation and \
                self.temp.key_cursors[id][1:3] == (row, col):
            bg_color = dim_cursor_color
        else:
            bg_color = temp_text_bg
        infer_tag = 'infer2' if self.sess.key_navigation else 'infer'
        for i in range(wlen):
            paint_cell_temp(grid, r, c, word[i], tags, bg=bg_color,
                            fg=preview_color, below=(i==0 and infer_tag),
                            over_block=cells[r+dr][c+dc][2])
            bg_color = temp_text_bg
            r += dir; c += 1-dir

        tlen = min(len(tail), size - r*dir - c*(1-dir))
        for i in range(tlen):
            paint_cell_temp(grid, r, c, tail[i], tags, bg=temp_text_bg,
                            fg=custom_red)
            r += dir; c += 1-dir
        if r < size and c < size:
            cell = cells[r+dr][c+dc]
            if cell[0] or cell[1]:
                paint_cell_border(grid, r+dr, c+dc, tags)
        if offset:    # optionally add an outline box around word
            paint_bounding_box(grid, dir, row, col, wlen, tags,
                               num_exists_color, 2, extent=offset+1)
        if pointer:
            paint_triangle_pointer(grid, dir, row, col, tags,
                                   num_exists_color)

# This version is simpler and safer for use in region movement operations
# and other cases where the intermediate states might be inconsistent.

    def paint_word_pre(self, id, dir, word, row, col, tags, color,
                       box=0, blocks=0):
        # temporary painting for preview, error uses
        if not word: return
        grid = self.gui.grids[id]
        r,c = row,col
        wlen = len(word)
        # first cell is handled separately so key cursor can show below
        if self.sess.key_navigation and \
                self.temp.key_cursors[id][1:3] == (row, col):
            bg_color = dim_cursor_color
        else:
            bg_color = temp_text_bg
        paint_cell_temp(grid, r, c, word[0], tags, bg=bg_color, fg=color)
        for i in range(1, wlen):
            r += dir; c += 1-dir
            paint_cell_temp(grid, r, c, word[i], tags,
                            bg=temp_text_bg, fg=color)
        if box:    # optionally add an outline box around word
            paint_bounding_box(grid, dir, row, col, wlen, tags, color, box)
        if blocks:
            paint_cell_border(grid, row-dir, col-1+dir, tags)
            paint_cell_border(grid, row+wlen*dir, col+wlen*(1-dir), tags)
