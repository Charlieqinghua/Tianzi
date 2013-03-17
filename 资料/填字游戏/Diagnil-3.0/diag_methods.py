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
from diag_classes   import *


# ---------- Class definitions ---------- #

class DiagMethods(object):
    def __init__(self, master=None): pass


# ---------- Misc application methods ---------- #

# Look up text in designated word entry and parse into number, word tuple.
# If entry is partial or empty, try to determine number and word by
# inferring from the grid, wordbox lookup or crossing letters.
# Also accommodate words with wildcards.
# If id != None, row and col must be present.
# Raises UserError if either number or word still missing after lookup.
# Raises FalseStart if no plausible word can be synthesized.

    def look_up_entry(self, dir, id=None, row=None, col=None,
                      use_wordbox=0, default_len=3):
        num, wild, word = parse_word(self.gui.word_ent[dir].get())  ### excep
        # num = -1 if number absent, word = '' if word absent
        # wild = 1 if wildcards present
        if isinstance(word, str):
            # separate word and any comma-separated alternatives
            word_alts = word.split(',')
            word, alts = word_alts[0], word_alts[1:]
        else:
            alts = []
        num_entry, word_entry = num >= 0, word   # flags for user-typed fields
        if num < 0:
            if id == None:
                if word != '':
                    # if no number, use autoincrementing word number
                    num = self.temp.next_word_num[dir]
            elif self.sess.key_navigation and self.eph.est_cell_num_key:
                # give key cursor priority
                num = self.eph.est_cell_num_key    # will be 0 if key mode off
            elif not self.sess.key_navigation and self.eph.est_cell_num:
                num = self.eph.est_cell_num
            else:
                try:
                    num = self.infer_word_number(dir, id, row, col,
                                                 word != '')         ###
                except OffNominal:
                    pass
        if num > 0 and wild:           # wildcards among letters
            if id == None:
                raise_error(*error_msg_sub('bad_word_extension',
                                           self.gui.word_ent[dir].get()))
            else:
                # try to extend word using crossing grid letters
                num, word = self.form_full_word(dir, num, word, id, row, col)
        elif num > 0 and id != None and word != '':
            # no wildcards but possibly extendable using crossing grid letters
            num, word = self.form_full_word(dir, num, word, id, row, col)

        elif num > 0 and word == '':   # number only, look up word
            try:
                word = self.perm.words[dir][num]
                # suppress overwrite check by mimicking wordbox selection
                self.temp.sel_num_word[dir] = (0, '', None)
            except KeyError:
                # not on the list; try to make one up
                word = self.infer_letters_cross(dir, id, row, col)
                if word == '':
                    # if no word, but a wordbox entry is highlighted,
                    # and it's not gridded yet, then use it
                    sel_index = self.gui.wordbox[dir].curselection()
                    if use_wordbox and sel_index:
                        selection = self.gui.wordbox[dir].get(sel_index[0])[0]
                        # has form ('num', '-+# word sep clue')
                        symb, word_txt = \
                            selection[1].split(clue_separator)[0].split()
                        word_txt = word_txt.split(',')[0]  # strip off ',...'
                        if word_txt == null_word_symb:
                            word = None
                        else:
                            word_ent = selection[0] + ' ' + word_txt
                            wl_item = parse_wordlist_item(word_ent)
                            if self.perm.grid_id[dir].has_key(wl_item[0]):
                                word = None
                            else:
                                num, wild, word = wl_item
                    else:
                        word = None
        if word == None: raise FalseStart
        if (num <= 0) != (word == ''):
            # issue an error message when only one is missing, not both
            if num <= 0:
                user_dialog(showerror, *error_messages['no_word_number'])
            else:
                user_dialog(showerror, *error_msg_sub('no_word_letters',
                                                      (num, dir_text[dir])))
        if word and len(word) < 3:
            self.eph.warnings['word_too_short'] = word
        if (num <= 0) or (word == ''): raise UserError
        return num, word, alts, num_entry, word_entry


# ---------- Word number inference ---------- #

# Try to infer number for a new word based on position of first letter
# (row,col).  If we can't discern a plausible number, issue an exception.
# Only considers cells in given grid.  Call only when id is valid.
# Returns word number (>= 1), or 0 / None / False to indicate failure.

    def infer_word_number(self, dir, id, row, col, check=0, need_unique=0):
        # user can turn this feature off completely
        if not app_prefs['infer_nums']: raise OffNominal
        if check:
            def sorry():
                if row != None:
                    paint_cell_marker(self.gui.grids[id], row, col)
                    raise OffNominal
                else:
                    raise_error(*error_messages['cannot_infer_number'])
        else:
            def sorry(): raise OffNominal

        cells = self.aux.cells[id]
        cell = cells[row][col]
        if cell[2]: sorry()    # cell occupied by block
        try:
            prev_cell = cells[row-1][col] if dir else cells[row][col-1]
            if prev_cell[0] or prev_cell[1]:
                # reject if non-head cell or crossing word above/left -- excep
                sorry()
        except IndexError:
            pass           # top row or leftmost column => OK
        i, j = row, col
        if dir == 0 and \
           (j > grid_size[id] - 3 or cells[i][j+1][2] or cells[i][j+2][2]) \
           or dir == 1 and \
           (i > grid_size[id] - 3 or cells[i+1][j][2] or cells[i+2][j][2]) :
            sorry()               # not enough room for word
        return self.word_num_est(id, dir, (row, col), need_unique) or 0

# Estimate word number by first finding the max lower head cell and the
# min upper head cell.  Then divide rows between the two into two regions.
# First region scans up from max lower; second region scans down from min
# upper.  Choose one based on which region target row lies.  In some cases,
# apply interpolation or extrapolation to get a more realistic estimate.

    def word_num_estimate(self, id, dir, target, need_unique=0):
        # target is a cell (r,c)
        grid_posns = self.perm.posns[id]     ## [dir -> {num -> (r,c)}]
        cells = self.aux.cells[id]
        posn_items = [ grid_posns[d].items() for d in 0,1 ]
        # check if target is a head cell (needed in case words out of order;
        # make sure number is recognized for head cells)
        heads = reduce(add, [ filter(lambda p: p[1] == target, items)
                              for items in posn_items ] )
        if heads: return heads[0][0]      # should be at most 2 (same num)

        lower_a_items = [ p for p in posn_items[0] if p[1] < target ]
        lower_d_items = [ p for p in posn_items[1] if p[1] < target ]
        upper_a_items = [ p for p in posn_items[0] if p[1] > target ]
        upper_d_items = [ p for p in posn_items[1] if p[1] > target ]
        lower_a_max = max(lower_a_items + [(0,(0,-1))])
        lower_d_max = max(lower_d_items + [(0,(0,-1))])
        lower_max = max(lower_a_max, lower_d_max)

        lower_est = self.lower_num_est(id, dir, target, grid_posns, cells,
                                       lower_a_items, lower_d_items,
                                       lower_a_max, lower_d_max)
        upper_est = 10000

        if upper_a_items or upper_d_items:
            min_upper_a = min(upper_a_items + [(10000,(0,0))] )
            min_upper_d = min(upper_d_items + [(10000,(0,0))] )
            upper_min = min(min_upper_a, min_upper_d)
            delta = upper_min[1][0] - lower_max[1][0]       # diff in rows
            upper_est = self.upper_num_est(id, dir, target,
                                           grid_posns, cells, delta,
                                           lower_max, upper_min)
            use_proximity = 1
            if upper_est == lower_est:
                est = lower_est
            elif need_unique:
                return 0
            elif lower_max[0] == 0:        # no lower word
                lower_est = 0              # no floor for selection
                if id == 0:
                    est = max(0, upper_est)    # descend gradually
                else:
                    # minigrids: lower end not anchored
                    est = extrapolated_word_number(upper_min[0], upper_min[1],
                                                   target)
                    est = min(max(1, est), upper_est)
                    use_proximity = 0
            elif upper_est < lower_est:
                return 0
            elif lower_max[1][0] >= target[0] - 1:
                est = lower_est
            elif target[0] + 1 >= upper_min[1][0]:
                est = upper_est
            else:
                # if target lies within a wide gulf of multiple rows,
                # interpolate target num between lower and upper
                est = interpolated_word_number(
                          lower_max[0], lower_max[1], target, *upper_min)
                est = min(max(est, lower_est), upper_est)
            if use_proximity:
                est = self.prox_limited_num(id, target, lower_max, upper_min,
                                            lower_est, upper_est, est)

        elif need_unique:    # open-ended -> not constrained enough
            return 0
        elif lower_max[1][0] >= target[0] - 1:
            # if no upper words and target is close, just use lower_est
            est = lower_est
        else:
            # if no upper words, try to augment estimated word number based
            # on word number curve; it's only used if it exceeds current
            # estimate, as would happen far down the grid
            est = extrapolated_word_number(lower_max[0], lower_max[1], target)
            est = max(est, lower_est)

        if not est: return est

        # in clueful mode, number estimates should be constrained to be
        # among the known clue numbers
        if self.temp.puz_defn:
            num = select_actual_number(self.temp.puz_defn.nums[dir],
                                       lower_est, est, upper_est)
        else:
            num = est
        return num


# Method word_num_est normally masks uncaught exceptions to minimize the
# impact of residual bugs.  When debug flag is on, allow the exceptions
# to pass through and go to top-level exception handler.

    if check_assertions:
        word_num_est = word_num_estimate
    else:
        def word_num_est(self, id, dir, target, need_unique=0):
            try:
                return self.word_num_estimate(id, dir, target, need_unique)
            except:
                trace = StringIO()
                print_exc(100, trace)
                debug_log("\n***** word_num_est %s raised an exception. "
                          "*****\n%s" % ([id, dir, target], trace.getvalue()))
                return 0    # default is null word number


# Try to find the minimum word number implied by the structure of a
# grid up through target cell.  Start by finding the highest numbered
# head cell of either direction preceding target.  If there is an
# Across word here, scan further to count each cell having a block in
# the row above.  Then count apparent word regions until target reached.

    def lower_num_est(self, id, dir, target, grid_posns,
                      cells, a_items, d_items, max_a, max_d):
        if a_items:
            across_word = self.perm.words[0][max_a[0]]
        else:
            across_word = ''
        aword_len = len(across_word)

        # unless max down word is past end of max across word,
        # start with a pre-scan of max across word
        if max_d[1] < (max_a[1][0], max_a[1][1] + aword_len):
            num, (i,j) = max_a
            interior_down = (max_a[1] < max_d[1]) and max_d
        else:
            num, (i,j) = max_d
            across_word = ''     # disable pre-scan
        # i,j current cell; num is estimate up to cell (i,j)

        # first count down-word heads within last across word
        if across_word:
            j0 = j
            if i < target[0]: limit = j + aword_len
            else:             limit = min(target[1] + 1, j + aword_len)

            # first do a look-ahead scan to find current and later down heads
            if i == 0 == id or num == 1:
                # on row 0 of main grid or word 1; all cells will be down heads
                dh = [1] * aword_len
            elif id > 0 and i == 0:
                # on row 0 of mini-grid; can't assume anything about row above
                dh = [0] * aword_len
            else:
                # where prev row has a block above, cells will be down heads
                dh = [ cells[i-1][jj][2] and 1              # i > 0
                       for jj in range(j, j + aword_len) ]
                # find future down heads implied by current structure,
                # assuming two blocks can't be separated by only 1 or 2
                # letters (min word size = 3)
                jj, jj_max = 0, aword_len - 2
                dh.append(0)        # dummy for jj+3 case at loop end
                while jj < jj_max:
                    fill = dh[jj] and ( dh[jj+3] and (1,1) or 
                                        dh[jj+2] and (1,)    )  or ()
                    dh[jj+1 : jj+1+len(fill)] = fill
                    jj += len(fill) + 1

            # if the max down word is interior to the across word,
            # go directly to that position
            if interior_down:
                num = interior_down[0]
                j = interior_down[1][1]
            adjust_num = 1               # increment in next cell

            # now scan across word and increment inferred word number;
            # num records the high water mark
            for jj in range(j+1, limit):
                num += adjust_num        # adjustment from previous cell
                # if this cell is or will be a down-word head, it should
                # get a higher word number
                adjust_num = dh[jj - j0] or 0    # ensure it's numeric

            in_word = 0       # start fresh in next phase
            j = limit         # advance to end of word or target
        else:
            # no pre-scan when max down word is past max across word
            adjust_num = 1       # last cell was a down head
            in_word = 1          # part of a future across word
            j += 1

        # at this point, j is the column of the next cell; it is just past
        # the start of the max numbered down word (or end of the highest
        # across word); num is the lowest number that can be given to cell
        # (i,j-1); adjust_num is 1 if num needs to be incremented in the
        # next cell;

        # now scan across, looking for alternating sequences of letters and
        # word separators, where empty cells are ignored
        grid_width = grid_size[id]
        cell_row = cells[i]
        row_empty = 0                      # first row had one head cell
        while (i,j) <= target:
            num += adjust_num              # adjustment from previous cell
            adjust_num = 0
            if j >= grid_width:            # wrap around to next row
                i += 1
                cell_row = cells[i]
                adjust_num = row_empty     # at least one new number per row
                j, in_word = 0, 0
                row_empty = 1
            if cell_row[j][2]:             # hit a block; across word ends
                in_word = 0
            elif cell_row[j][1] and not in_word:   # new down letter
                adjust_num, in_word = 1, 1
                row_empty = 0
            j += 1
        return num

# Other scan works backward toward target cell.  Try to find the maximum
# word number implied by the structure of a grid down through target cell. 
# Do not call when both a_items, d_items are empty.

    def upper_num_est(self, id, dir, target, grid_posns, cells,
                      delta_rows, lower_max, upper_min):
        # scan across backwards, looking for alternating sequences of
        # letters and word separators, where empty cells are ignored
        upper_num, (i,j) = upper_min
        num_gap = upper_num - lower_max[0] - 1   # word number slots
        if num_gap <= 0: return 0
        num = upper_num - 1
        j -= 1     # i,j current cell; num is cumulative estimate
        adjust_num = 0
        in_word = 0    ### target could be start of across word

        # following scan is the same as in lower_num_est, only in reverse
        grid_last = grid_size[id] - 1
        cell_row = cells[i]
        row_empty = 0                      # first row had one head cell
        while (i,j) >= target:
            num -= adjust_num        # account for start of word
            adjust_num = 0
            if j < 0:                # wrap around to end of previous row
                adjust_num = in_word or row_empty
                i -= 1
                cell_row = cells[i]
                j = grid_last
                in_word = 0
                row_empty = 1
            if cell_row[j][2] and in_word:    # hit a block; across word ends
                in_word = 0
                adjust_num = 1
            elif cell_row[j][1]:              # new down letter
                in_word = 1
                row_empty = 0
            j -= 1
            # target not in down word so adjust_num already counted

        if upper_num - num > num_gap:
            return 0               # not enough room

        return num

# Apply constraints on number estimates based on how close the target is
# to the bracketing numbered cells.  Exclude existing blocks from the
# distance calculations.  Use the target position to bound the word number
# estimate.  Example: target one cell past lower_max, means the number
# can't exceed L+1.

    def prox_limited_num(self, id, target, lower_max, upper_min,
                         lower_est, upper_est, est):
        if lower_max[1][0] + 1 < upper_min[1][0]:
            return est    # more than one row apart -> don't bother
        lower_num, (lower_row, lower_col) = lower_max
        upper_num, (upper_row, upper_col) = upper_min
        if lower_row == upper_row:
            blocks1 = self.num_blocks_row(id, lower_max[1], target)
            blocks2 = self.num_blocks_row(id, target, upper_min[1])
            lower_offset = target[1] - lower_col - blocks1
            upper_offset = upper_col - target[1] - blocks2
        else:
            if id == 0 and self.temp.size_symm[0]:
                width = self.temp.size_symm[3]
            else:
                width = grid_size[id]
            if lower_row == target[0]:
                blocks1 = self.num_blocks_row(id, lower_max[1], target)
                blocks2 = self.num_blocks_row(id, target, (lower_row, width)) \
                          + self.num_blocks_row(id, (upper_row, -1),
                                                upper_min[1])
                lower_offset = target[1] - lower_col - blocks1
                upper_offset = upper_col + width - target[1] - blocks2
            else:
                blocks1 = self.num_blocks_row(id, lower_max[1],
                                              (lower_row, width)) \
                          + self.num_blocks_row(id, (upper_row, -1), target)
                blocks2 = self.num_blocks_row(id, target, upper_min[1])
                lower_offset = target[1] + width - lower_col - blocks1
                upper_offset = upper_col - target[1] - blocks2

        num = min(min(lower_num + lower_offset, upper_est),
                  max(est, max(upper_num - upper_offset, lower_est)))
        return num
    

# Find word number either as digits typed in a word entry or as estimated
# word number from the current grid cell.  Raises OffNominal if none.

    def get_word_num(self, dir):
        try:
            num, wild, word = parse_word(self.gui.word_ent[dir].get())  ###
        except UserError:
            raise OffNominal
        if num < 0:
            if self.sess.key_navigation:
                # use key cursor value
                num = self.eph.est_cell_num_key
            else:
                # use mouse cursor value
                num = self.eph.est_cell_num
        if not num: raise OffNominal
        return num


# ---------- Word and grid services ---------- #

# Derive a word from grid letters by combining typed word fragments with
# interspersed wildcards representing grid fragments.  Stop at first
# placeholder char when scanning for fragments.  Append a tail by
# matching crossing letters that follow the word.
# Returns (num, word).

    def form_full_word(self, dir, num, frags, id, row, col):
        word = ''
        for f in frags:
            new = f
            if f == '*':
                if row < grid_size[id] and col < grid_size[id] and \
                   self.aux.cells[id][row][col][dir]:
                    enum = self.aux.cells[id][row][col][dir][0]
                    if enum != num:
                        num = enum    # overriding inferred or supplied num
                        self.eph.warnings['extension_num_override'] = 1
                    # suppress overwrite check when extending word:
                    self.temp.sel_num_word[dir] = (0,'',None)
                new = self.infer_letters_either(dir, id, row, col)
            word += new
            row += len(new) * dir
            col += len(new) * (1-dir)
        # after loop, row & col point to next cell after word
        tail = self.infer_letters_cross(dir, id, row, col)
        return num, word + tail

# Derive a word from grid letters and word entry so a temporary word
# display can be pasted on the grid.  Returns (num, word, tail).

    def form_full_word_temp(self, dir, entry_text, id, row, col):
        try:
            num, wild, frags = parse_word(entry_text, 0)  ### excep
        except UserError:
             # bad word entry, return error indicator
            return -1, '#' * len(entry_text), ''
        word = ''
        if wild:    # combine fragments into a single string
            frags = reduce(lambda x,y: x+y, frags, '')
        if not frags: return num, '', ''
        for f in frags:   # pick up crossing letters at end
            new = f
            if f == '*':
                new = self.infer_letters_either(dir, id, row, col)
            elif f == '?':
                new = self.infer_letters_either(dir, id, row, col)[:1]
                if new == '': new = '?'
            word += new
            row += len(new) * dir
            col += len(new) * (1-dir)
        # after loop, row & col point to next cell after word
        tail = self.infer_letters_cross(dir, id, row, col)
        return num, word, tail

# Collect first N contiguous letters already pasted on the grid in
# either direction.  If N = 0, return ''.  Placeholder chars do not
# count as letters.  Preference is given to letters in aligned direction.

    def infer_letters_either(self, dir, id, row, col):
        cells = self.aux.cells[id]
        new_word = ''
        try:
            cell_rc = cells[row][col]
            while cell_rc[dir] or cell_rc[1-dir]:
                if cell_rc[dir] and cell_rc[dir][2] != placeholder:
                    new_word += cell_rc[dir][2]  # append letter
                elif cell_rc[1-dir] and cell_rc[1-dir][2] != placeholder:
                    new_word += cell_rc[1-dir][2]
                else: break
                row += dir; col += 1-dir
                cell_rc = cells[row][col]
        except IndexError:
            pass            # reached end of row/col
        return new_word

# Try to infer a word from crossing letters already pasted on the grid.
# Look for first N contiguous letters in designated direction.
#  If cell has a block, return ''.

    def infer_letters_cross(self, dir, id, row, col):
        if id == None: return ''
        cells = self.aux.cells[id]
        new_word = ''
        try:
            while cells[row][col][1-dir]:
                new_word += cells[row][col][1-dir][2]  # append crossing letter
                row += dir; col += 1-dir
        except IndexError:
            pass            # reached end of row/col
        return new_word

# Update a word using crossing letters already pasted on the grid.  Any
# clashes are resolved in favor of crossing letters.  Word is assumed to
# lie on a grid already, so there is no overflow.

    def merge_with_crossing(self, dir, word, id, row, col):
        cells = self.aux.cells[id]
        new_word = ''
        for c in word:
            if cells[row][col][1-dir]:
                cross_char = cells[row][col][1-dir][2]
                if cross_char == placeholder: new_word += c
                else:                         new_word += cross_char
            else:
                new_word += c
            row += dir; col += 1-dir
        return new_word
    
# Replace placeholder characters with crossing letters already pasted
# on the grid.  Word is assumed to lie on a grid already, so there is
# no overflow.

    def replace_placeholders(self, dir, word, id, row, col):
        cells = self.aux.cells[id]
        new_word = ''
        for c in word:
            if c == placeholder and cells[row][col][1-dir]:
                new_word += cells[row][col][1-dir][2]
            else:                         
                new_word += c
            row += dir; col += 1-dir
        return new_word

# Try to infer a search pattern from letters already pasted on the grid.
# First, find a single letter, skipping over empty cells.  Then look for
# a second letter.  If adjacent, keeping scanning to return the maximum
# contiguous sequence.  If blank cells lie between, place a wildcard before
# the second letter.  If > 8 blanks, use just a single-letter pattern.
# A block terminates the process at any point.

    def infer_search_pattern(self, dir, id, row, col):
        if id == None: return ''
        cells = self.aux.cells[id]
        pattern = ''; blanks = 0
        try:
            while cells[row][col] == null_cell:   # scan past initial blanks
                row += dir; col += 1-dir
            if cells[row][col][2]: return ''
            if cells[row][col][0]: pattern += cells[row][col][0][2]
            else:                  pattern += cells[row][col][1][2]
            row += dir; col += 1-dir
            while cells[row][col] == null_cell: # scan past intervening blanks
                blanks += 1
                row += dir; col += 1-dir
            if blanks > 8: return pattern
            while cells[row][col][0] or cells[row][col][1]:
                if cells[row][col][0]: pattern += cells[row][col][0][2]
                else:                  pattern += cells[row][col][1][2]
                row += dir; col += 1-dir
        except IndexError:
            pass            # reached end of row/col
        if blanks == 0 or len(pattern) < 2: return pattern
        return pattern[0] + '*' + pattern[1:]

# Determine the relative index within a word of the letter at a given cell.
# Assumes the word is on the indicated grid.

    def letter_index(self, dir, id, row, col):
        posns = self.perm.posns[id][dir]
        num = self.aux.cells[id][row][col][dir][0]
        return (row,col)[1-dir] - posns[num][1-dir]

# Search for grid and cell location currently under the mouse cursor.

    def find_grid_cell(self):
        px, py = self.master.winfo_pointerxy()
        for id in range(num_grids):    # find id of selected grid
            grid = self.gui.grids[id]
            try:
                if grid == self.master.winfo_containing(px, py): break
            except:
                pass    # lookup sometimes fails
        else:
            return ()
        x, y = self.gui.map_grid_posn[id](px - grid.winfo_rootx(),
                                          py - grid.winfo_rooty())
        limit = grid_size[id] - 1
        row = min(y // cell_size, limit) 
        col = min(x // cell_size, limit)
        return grid, id, row, col


# Check if the letters of a new word can complete any crossing words.
# Assumes the new word already passed its checks and has no conflicts.
# Potential crossing words are contiguous sequences of cells having
# letters in the current direction but no existing letters in the
# crossing direction.  Each sequence must be terminated at both ends by
# a block or grid edge.  The numbers for the crossing words must be
# inferred, so failure to find a number drops it from the candidates.
# Return a list of (num, word, row, col) tuples for new crossing words
# to be entered.  Otherwise, return empty list.

    def cross_completions(self, dir, wlen, id, row, col):
        cells = self.aux.cells[id]
        if not cells[row][col][dir]:
            return []        # no letter in current direction
        if id == 0 and self.temp.size_symm[0]:
            width, height = self.temp.size_symm[3:5]
        else:
            width = height = grid_size[id]
        cross_words = self.perm.words[1-dir]
        cross_posns = self.perm.posns[id][1-dir]
        comp_words = {}
        for r, c in generate_cells(dir, wlen, row, col):
            if (c, r)[dir] >= (width, height)[dir]:
                break        # word extends past boundary
            if cells[r][c][2] or cells[r][c][1-dir]:
                continue     # at a block or crossing word already exists

            # scan backward to find first half of candidate word
            xr, xc = r - (1-dir), c - dir
            first = []
            while xr >= 0 and xc >= 0 and \
                    not cells[xr][xc][1-dir] and cells[xr][xc][dir]:
                first.append(cells[xr][xc][dir][2])
                xr -= 1-dir
                xc -= dir
            if xr >= 0 and xc >= 0 and not cells[xr][xc][2]:
                continue         # left/top end not a block
            start = (xr + (1-dir), xc + dir)

            # scan forward to find second half of candidate word
            xr, xc = r + (1-dir), c + dir
            second = []
            while xr < height and xc < width and \
                    not cells[xr][xc][1-dir] and cells[xr][xc][dir]:
                second.append(cells[xr][xc][dir][2])
                xr += 1-dir
                xc += dir
            if xr < height and xc < width and not cells[xr][xc][2]:
                continue     # right/bottom end not a block
            try:
                num = self.infer_word_number(1-dir, id, *start, need_unique=1)
                if not num: continue
            except OffNominal:
                continue
            # found a suitable word number; candidate is usable
            cross_word = ''.join(reversed(first)) + \
                         cells[r][c][dir][2] + ''.join(second)
            # later words overwrite earlier ones having the same number;
            # this is less likely to produce wrongly numbered words when
            # the inference algorithm is off a little
            comp_words[num] = (num, cross_word, start[0], start[1])
        return comp_words.values()


# Find the number of blocks between cells c and d (exclusive).
# c, d are assumed to be on the same row.  Any empty cells or pairs of
# empty cells between blocks will be counted as blocks.

    def num_blocks_row(self, id, c, d):
        row = c[0]
        if d[0] != row: return 0
        is_block = [ int(cell[2] != None)
                     for cell in self.aux.cells[id][row][1+c[1]:d[1]] ]
        dist_prev = 3
        for i in range(len(is_block)):
            if is_block[i]:
                if 1 <= dist_prev <= 2:
                    is_block[i-1] = 1
                if dist_prev == 2:
                    is_block[i-2] = 1
                dist_prev = 0
            else:
                dist_prev += 1
        return sum(is_block)


# ---------- Support for key-cursor motion ---------- #

# Find next free cell (not occupied by a block) in given direction
# suitable for placing grid entry cursor.  Wrap around to next row/col
# as needed.
# When abs(delta) > 1, as with Tab command, move to the next cell
# likely to start a new word.

    def next_free_cell(self, id, dir, row, col, delta=0):
        if id == 0 and self.temp.size_symm[0]:
            width, height = self.temp.size_symm[3:5]
        else:
            width = height = grid_size[id]
        if not (0 <= row < height and 0 <= col < width):
            width = height = grid_size[id]
        cells = self.aux.cells[id]
        neg_delta = delta < 0

        def blocked_cells(scan_dir, i, skip_short=0, skip_letters=0):
            # scan row or column for blocks and return list of same length
            # with flag set for each cell that is a block;
            # when skip_letters holds, skip (mark as blocked) those
            # cells having aligned letters;
            # when skip_short holds, mark a cell blocked if it lies
            # in a segment of empty cells shorter than length 3;
            length = height if scan_dir else width
            prev_letter = False
            blocked, lettered = [], []
            for k in range(length):
                if scan_dir: cell = cells[k][i]
                else:        cell = cells[i][k]
                # allow head-cell letters but not others:
                lettered.append(skip_letters and cell[scan_dir]
                                and prev_letter)
                prev_letter = cell[scan_dir]
                blocked.append(cell[2])    # block flag

            if skip_short:
                blocked.append(True)     # force handling of last cells
                num_free = 0             # number of consecutive empty cells
                for k in range(length+1):
                    if blocked[k]:
                        if num_free == 1:
                            blocked[k-1] = True
                        elif num_free == 2:
                            blocked[k-1] = blocked[k-2] = True
                        num_free = 0
                    else:
                        num_free += 1
                del blocked[-1]
            return [ b or l for b, l in zip(blocked, lettered) ]

        def end_run(r, c, delta, align_prev=0):
            # find cell past last of a contiguous run of blocks;
            # optionally align with head of a nearby word
            if delta == 0:
                delta = 1              # force forward excursion on set action
            else:
                r += dir * delta       # advance by one initially
                c += (1 - dir) * delta
            if dir == 1 and 0 <= c < width:
                blocked = blocked_cells(dir, c)
                while 0 <= r < height and blocked[r]:
                    r += delta
                if 0 <= r < height: return (r, c)
                else: return end_run(height if neg_delta else -1,
                                     c + delta, delta)
            elif dir == 0 and 0 <= r < height:
                blocked = blocked_cells(dir, r)
                while 0 <= c < width and blocked[c]:
                    c += delta
                if 0 <= c < width: return (r, c)
                else: return end_run(r + delta,
                                     width if neg_delta else -1, delta)
            else:
                return None   # cross-direction value out of bounds

        def prev_next_word(x, y, wdir, sign):
            # find posn, num for prev, next across/down words
            p_items = self.perm.posns[id][wdir].items()
            if wdir:
                posns = [ (p[1], p[0], n) for n,p in p_items ]
            else:
                posns = [ (p[0], p[1], n) for n,p in p_items ]
            head_num = sign * 10000
            try:
                # if x,y is a head cell, want x,y to be prev
                wx, wy, wn = max([ p for p in posns if p < (x, y, head_num) ])
                wend = wy + len(self.perm.words[wdir][wn])
                prev_word = wx, wy, wend
            except ValueError:
                prev_word = None    # no valid word in this direction
            try:
                # if x,y is a head cell, don't want x,y to be next
                wx, wy, wn = min([ p for p in posns if p > (x, y, head_num) ])
                wend = wy + len(self.perm.words[wdir][wn])
                next_word = wx, wy, wend
            except ValueError:
                next_word = None
            return prev_word, next_word

        def find_min_free(index, n, low, high, blocked, sign):
            # find first contiguous sequence of empty cells of length n
            k = index
            while low <= k < high:
                # scan alternating segments of blocks and free cells
                while low <= k < high and blocked[k]: k += sign
                start = k
                while low <= k < high and not blocked[k]: k += sign
                if abs(k - start) >= n: return start
            if k < 0 < index and \
                    all([ not blocked[i] for i in range(index+1) ]):
                return 'begin'    # not enough room -> use start of row/col
            return None
            
        def next_across_down(x, y, wdir, sign, need, jump, pn_prev, pn_next):
            # skip to next likely across/down word head
            # x,y are r,c for Across, and c,r for Down
            if not (0 <= x < (width if wdir else height)):
                return None    # row/col out of bounds
            y_extent = height if wdir else width
            blocked = blocked_cells(wdir, x, skip_short=1, skip_letters=1)
            if sign > 0:
                # x == pn_prev[0] ==> y >= pn_prev[1]
                if pn_prev and x == pn_prev[0] and y < pn_prev[2]:
                    y = pn_prev[2] + 1   # within word; skip past word end
                    jump = 0             # use first col/row if enough room
                else:
                    need += jump         # between words; need room to jump
                if pn_next and x == pn_next[0]:
                    limit = pn_next[1] - 1    # next word on same row/col
                else:
                    limit = y_extent
                start = find_min_free(y, need, 0, limit, blocked, sign)
                if start != None and start > y and jump > 0:
                    # have room at later start but 3 cells would suffice
                    start = find_min_free(start, 3, 0, limit, blocked, sign)
                    jump = 0
                elif start == None and need > 3:
                    # no room; settle for 3 instead
                    start = find_min_free(y+3, 3, 0, limit, blocked, sign)
                    jump = 0
                if start != None:
                    return x, start + jump        # enough free space
                elif pn_next and x == pn_next[0]:
                    return pn_next[:2]            # next word on this row/col
                else:
                    # go to next/prev row/col
                    return next_across_down(x + sign, 0, wdir, sign, 3, 0,
                                            pn_prev, pn_next)
            else:
                # x == pn_next[0] ==> y < pn_next[1]
                if pn_prev and x == pn_prev[0] and pn_prev[1] < y < pn_prev[2]:
                    return pn_prev[:2]   # within word; go to to start
                # between words; need room to jump
                if pn_prev and x == pn_prev[0]:
                    limit = pn_prev[2]       # prev word on same row/col
                else:
                    limit = 0
                start = find_min_free(y, max(need, jump+1), limit, y_extent,
                                      blocked, sign)
                if start == None and jump > 2:
                    # no room for 4; settle for 3 but jump to start of triple
                    start = find_min_free(y, 3, limit, y_extent, blocked, sign)
                    jump = 2
                if start == 'begin':
                    return x, 0   # not enough space, but near start of row/col
                elif start != None:
                    return x, start - jump   # enough free space
                elif pn_prev and x == pn_prev[0]:
                    return pn_prev[:2]            # next word on this row/col
                else:
                    # go to next/prev row/col
                    return next_across_down(x + sign, y_extent - 1, wdir,
                                            sign, 3, 2, pn_prev, pn_next)

        if abs(delta) > 1:
            sig_d = signum(delta)
            if dir:
                next = next_across_down(col, row, 1, sig_d, 3, 4,
                                        *prev_next_word(col, row, 1, sig_d))
                if next: next = next[1], next[0]   # restore row, col order
            else:
                next = next_across_down(row, col, 0, sig_d, 3, 4,
                                        *prev_next_word(row, col, 0, sig_d))
        else:
            next = end_run(row, col, delta)
        if next: return next
        elif delta == 0: return None       # no free cell found
        else:    return row, col           # current already last one possible


# Collect key cursors to save for undo state.  Restore them after undo/redo.

    def nonperm_recovery_state(self):
        return copy.deepcopy(self.temp.key_cursors)

    def restore_nonperm(self, nonperm):
        self.temp.key_cursors = nonperm
        id = self.sess.focus_region - 2
        if id >= 0:
            self.set_key_cursor(posn=nonperm[id][1:3])

# Add or remove key cursors when key navigation mode is enabled or disabled.

    def change_key_nav_status(self, enabled):
        if enabled:
            pass
        else:
            for id in range(num_grids):
                self.gui.grids[id].delete('key_cursor')


# ---------- Listbox and word number utilities ---------- #

# Given a word number thought to be on the word list, look it up and
# scroll its listbox so it appears in mid-window. ###, then select it.
# If word number is not on list, scroll to approximate position.
# Scroll both listboxes. ###, but only set selection for sel_dir.
# Also display length info in status line: word length or room available.

    def scroll_listbox_num(self, sel_dir, num,
                           id=None, row=None, col=None):
        # id != None implies row != None and col != None
        puz_defn = self.temp.puz_defn
        for dir in (0,1):
            word_nums = self.perm.nums[dir]
            if puz_defn:
                listbox_nums = self.temp.puz_defn.nums[dir]
            else:
                listbox_nums = word_nums
            index = bisect_left_max(listbox_nums, num)
            listbox = self.gui.wordbox[dir]

            if dir != sel_dir:
                center_word_view(listbox, index)
            else:
                if puz_defn:
                    self.set_listbox_indicator(dir, num, index, see_index=1)
                    index = bisect_left_max(word_nums, num)
                if word_nums and num == word_nums[index]:
                    if not puz_defn:
                        self.set_listbox_indicator(dir, num, index,
                                                   see_index=1)
                    # word could have been deleted before this procedure
                    # was invoked (delayed using an after-call)
                    word_str = self.perm.words[dir].get(num, '')
                    if word_str:
                        # display length of word under cursor
                        status = '%s-%s :  %s letters' % \
                                 (num, dir_text[dir], len(word_str))
                        alt_word = self.merge_with_crossing(dir, word_str,
                                                            id, row, col)
                        if not placeholder_congruent(alt_word, word_str):
                            status += ',  crossing : %s' % alt_word.upper()
                        self.gui.status_line2['text'] = status
                elif id != None:
                    if not puz_defn:
                        self.clear_listbox_indicator(dir)
                        center_word_view(listbox, index)
                    cells = self.aux.cells[id]
                    k = 1
                    try:
                        # scan until block found
                        while not cells[row+k*dir][col+k*(1-dir)][2]: k += 1
                    except IndexError:
                        # reached end of row/col
                        if self.temp.size_symm:
                            # truncate to declared size
                            if dir:
                                k = self.temp.size_symm[4] - row
                            else:
                                k = self.temp.size_symm[3] - col
                        else:
                            k = 100       # ignore if size unavailable
                    # display cells available, unless there are too few
                    # or too many to mention (avoid nuisance messages)
                    if 5 < k < 26: room = 'Room for %s letters.' % k
                    else:          room = ''
                    self.gui.status_line2['text'] = room

# Method scroll_listbox normally masks uncaught exceptions to minimize the
# impact of residual bugs.  When debug flag is on, allow the exceptions
# to pass through and go to top-level exception handler.

    if check_assertions:
        scroll_listbox = scroll_listbox_num
    else:
        def scroll_listbox(self, sel_dir, num,
                           id=None, row=None, col=None):
            try:
                self.scroll_listbox_num(sel_dir, num, id, row, col)
            except:
                trace = StringIO()
                print_exc(100, trace)
                debug_log("\n***** scroll_listbox %s raised an exception. "
                          "*****\n%s" % ([sel_dir, num, id, row, col],
                                         trace.getvalue()))
                # default is no action


# Scroll listboxes based only on the location of the mouse cursor or
# explicit row and column numbers.

    def scroll_listbox_xy(self):
        location = self.find_grid_cell()
        if location:
            indexes = self.find_indexes_nearby(*location[1:])
            for dir in (0,1):
                center_word_view(self.gui.wordbox[dir], indexes[dir])

    def scroll_listbox_posn(self, id, row, col):
        indexes = self.find_indexes_nearby(id, row, col)
        for dir in (0,1):
            center_word_view(self.gui.wordbox[dir], indexes[dir])

# Adjust word numbers on +/- keys.  If cursor lies over a word panel,
# update word entry cue.  If over a grid, update cell number cues,
# at both mouse cursor and key cursor.  Delta is -1, 0 or +1.

    def adjust_word_number(self, dir, delta, see_index=1, location=None,
                           delay_factor=0):
        if self.perm.final: return
        next_num = lambda n, d: self.next_number(dir, n, d)
        word_ent = self.gui.word_ent[dir]
        num, rest = parse_number(word_ent.get())
        if delta != 0 and self.gui.wordbox[dir].curselection():
            self.gui.wordbox[dir].selection_clear(0, END)

        if num >= 0:      # first check for number in word entry
            new_num, index = next_num(num, delta)
            if delta != 0:
                # recreate only when number changes ###
                word_ent.delete(0, END)
                word_ent.insert(0, '%d %s' % (new_num, rest))
            if self.sess.focus_region == dir:    # over word panel
                self.set_listbox_indicator(dir, new_num, index, # save_new=1,
                                           see_index=see_index)
            elif self.sess.focus_region >= 2:    # over grid area
                self.show_word_number_grid(dir, new_num, index,
                                           see_index, location, delay_factor)
        elif self.sess.focus_region == dir:    # over word panel
            new_num, index = next_num(self.temp.next_word_num[dir], delta)
            self.temp.next_word_num[dir] = new_num
            self.gui.next_num[dir]['text'] = str(new_num)
            self.set_listbox_indicator(dir, new_num, index, # save_new=1,
                                       see_index=see_index)

        elif self.sess.focus_region >= 2:    # over grid area
            try:
                self.adjust_word_number_grid(dir, delta, next_num,
                                             see_index, location, delay_factor)
            except OffNominal:
                return           # number inference failed

    def show_word_number_grid(self, dir, new_num, index,
                              see_index, location, delay_factor):
        if not location:
            location = self.find_grid_cell()
            if not location: return          # should be found
        grid, id, row, col = location
        grid.delete('visit')

        # handle key cursor and mouse cursor cells separately
        if self.sess.key_navigation:
            num = 0
            grid.after_cancel(self.eph.visit_id)
            key_num = new_num
            row, col = self.temp.key_cursors[id][1:3]
            grid.delete('infer2')
            infer_fn = lambda *args: \
                           self.show_inferred_key(grid, id, dir, row,
                                                  col, key_num, 1)
            self.eph.visit_id = \
                grid.after(visit_delay * delay_factor,
                           EventHandler('Key move infer', infer_fn))
            if key_num == 0:
                self.gui.status_line2['text'] = ''
                scroll_fn = \
                    lambda *args: self.scroll_listbox_posn(id, row, col)
        else:
            key_num = 0
            num = new_num
            grid.delete('infer')
            if num:
                self.show_inferred(grid, id, dir, row, col, num, 1)
            else:
                scroll_fn = lambda *args: self.scroll_listbox_xy()

        if key_num or num:
            scroll_fn = lambda *args: \
                self.scroll_listbox(dir, key_num or num, id, row, col)
        else:
            self.clear_listbox_indicator(dir)
        grid.after_cancel(self.eph.scroll_id)
        self.eph.scroll_id = \
            grid.after(scroll_delay * delay_factor,
                       EventHandler('Grid move infer scroll', scroll_fn))

    def adjust_word_number_grid(self, dir, delta, next_num,
                                see_index, location, delay_factor):
        if not location:
            location = self.find_grid_cell()
            if not location: return          # should be found
        grid, id, row, col = location
        grid.delete('visit')
        if delta: delay_factor = 0

        # handle key cursor and mouse cursor cells separately
        if self.sess.key_navigation:
            num = 0
            grid.after_cancel(self.eph.visit_id)
            key_num = self.eph.est_cell_num_key
            row, col = self.temp.key_cursors[id][1:3]
            grid.delete('infer2')
            if not key_num:    # cell num not displayed
                try:
                    key_num = self.infer_word_number(dir, id, row, col)
                except OffNominal:
                    key_num = -1     # unsuitable as head cell
            if key_num > 0:
                key_num, index = next_num(key_num, delta)
                self.gui.next_num[dir]['text'] = str(key_num)
            if key_num >= 0:
                self.eph.est_cell_num_key = key_num
                infer_fn = lambda *args: \
                               self.show_inferred_key(grid, id, dir, row,
                                                      col, key_num, delta)
                self.eph.visit_id = \
                    grid.after(visit_delay * delay_factor,
                               EventHandler('Key move infer', infer_fn))
            key_num = max(0, key_num)
            if key_num == 0:
                self.gui.status_line2['text'] = ''
                scroll_fn = \
                    lambda *args: self.scroll_listbox_posn(id, row, col)
        else:
            key_num = 0
            num = self.eph.est_cell_num
            grid.delete('infer')
            if not num:    # cell num not displayed
                try:
                    num = self.infer_word_number(dir, id, row, col)
                except OffNominal:
                    num = 0     # unsuitable as head cell
            if num:
                num, index = next_num(num, delta)
                self.show_inferred(grid, id, dir, row, col, num, delta)
                self.eph.est_cell_num = num
                # if delta != 0, indicate that user has set number estimate
                self.eph.keep_est_cell_num = delta
            else:
                self.eph.est_cell_num = 0
                scroll_fn = lambda *args: self.scroll_listbox_xy()

        if key_num or num:
            scroll_fn = lambda *args: \
                self.scroll_listbox(dir, key_num or num, id, row, col)
        else:
            self.clear_listbox_indicator(dir)
        grid.after_cancel(self.eph.scroll_id)
        self.eph.scroll_id = \
            grid.after(scroll_delay * delay_factor,
                       EventHandler('Grid move infer scroll', scroll_fn))

# Find next available word number when delta is -1, 0 or +1.  Also return
# index of next word number in listbox if it exists, None if it doesn't.

    def next_number(self, dir, cur_num, delta):
        if self.temp.puz_defn:
            clue_nums = self.temp.puz_defn.nums[dir]
            index = bisect_left_max(clue_nums, cur_num)
            if cur_num < clue_nums[index]:    # between clue numbers
                if delta < 0:
                    index = max(0, index - 1)
            else:
                index = max(0, min(index + delta, len(clue_nums) - 1))
            return (clue_nums[index], index)
        else:
            word_nums = self.perm.nums[dir]
            new_num = max(1, cur_num + delta)
            index = bisect_left(word_nums, new_num)
            if not (0 <= index < len(word_nums)) or \
                    new_num < word_nums[index]:  # not in word nums
                index = None
            return (new_num, index)

# Find index within listbox for given word number.  Return None if absent.

    def wordbox_index(self, dir, num):
        if self.temp.puz_defn:
            num_list = self.temp.puz_defn.nums[dir]
        else:
            num_list = self.perm.nums[dir]
        index = bisect_left(num_list, num)
        if index < len(num_list) and num == num_list[index]:
            return index
        else:
            return None

# Change highlighting in word/clue listboxes.  Clear old one and set
# new one or leave off if none available.  The old item is identified by
# word number and index.  Because index values can change in clueless mode
# as words are added and deleted, the current index needs to be found by
# searching the list of word numbers.

    def set_listbox_indicator(self, dir, new_num=None, new_index=None,
                              see_index=0):
        if self.temp.puz_defn:
            cur_num, cur_index = self.temp.indicator_cur[dir]
        else:
            cur_num = self.temp.indicator_cur[dir][0]
            cur_index = self.wordbox_index(dir, cur_num)

        wordbox = self.gui.wordbox[dir]
        size = wordbox.size()
        config = lambda i,c: wordbox.itemconfigure(i, bg=c)
        if cur_index != None:
            for ndx in range(size):
                config(ndx, '')     # clear every indicator

        self.temp.indicator_cur[dir] = new_num, new_index
        if new_index != None and new_index < size:
            # set new indicator
            config(new_index, listbox_indicator)
            if see_index:
                center_word_view(self.gui.wordbox[dir], new_index, 0.45)

    def clear_listbox_indicator(self, dir):
        wordbox = self.gui.wordbox[dir]
        config = lambda i,c: wordbox.itemconfigure(i, bg=c)
        for ndx in range(wordbox.size()):
            config(ndx, '')     # clear every possible indicator


# Adjust temporary word display if cursor lies over a grid.

    def adjust_temp_word_display(self, dir, entry_text):
        if self.perm.final: return
        id = self.sess.focus_region - 2
        if id < 0: return        # not over grid area
        if self.eph.preview > 0 or self.eph.multistep_mode: return
        if self.sess.key_navigation:
            grid = self.gui.grids[id]
            row, col = self.temp.key_cursors[id][1:3]
        else:
            location = self.find_grid_cell()
            if not location: return          # should be found
            grid, id, row, col = location
        grid.delete('preview')             # retain inferred number display
        if entry_text == '': return
        if ',' in entry_text:
            entry_text = entry_text.split(',')[0]    # rest are alternatives
        num, word, tail =\
             self.form_full_word_temp(dir, entry_text, id, row, col)
        if word == '' and num > 0:
            try:
                word = self.perm.words[dir][num]
            except KeyError:
                pass   # OK: no word for this number
        self.paint_word_temp(id, dir, word, tail, row, col, ('preview',))

# Slide word listboxes so that each center word is approximately nearest
# to the cell at row,col.

    def adjust_wordboxes(self, id, row, col):
        limit = grid_size[id] - 1
        row = min(row, limit)   # catch excess at right edge line
        col = min(col, limit)
        indexes = self.find_indexes_nearby(id, row, col)
        for d in (0,1):
            center_word_view(self.gui.wordbox[d], indexes[d])

# Save current yview positions of wordboxes for later restoration.

    def snap_wordbox_yview(self):
        self.eph.wordbox_yview = \
            [ self.gui.wordbox[d].yview()[0] for d in (0,1) ]

# Clear selection and related state information

    def clear_wordbox_selection(self, dir):
        self.gui.wordbox[dir].selection_clear(0, END)
        self.gui.word_ent[dir].delete(0, END)
        self.sess.word_entry_text[dir] = ''


# A search for nearby words is conducted by finding Across words
# that bracket the target cell.  The word numbers are interpolated
# to estimate indexes into the word number lists.
# A pair of listbox indexes is returned.

    def find_indexes_nearby(self, id, row, col):
        if self.temp.puz_defn:
            anums, dnums = self.temp.puz_defn.nums
        else:
            # clueless mode: only entered words are present
            anums, dnums = self.perm.nums

        posn_items = self.perm.posns[id][0].items()
        target = row, col
        matches = [ p for p in posn_items if p[1] == target ]
        if matches:
            num = matches[0][0]
            return anums.index(num), bisect_left_max(dnums, num)

        lower_a_items = [ p for p in posn_items if p[1] < target ]
        upper_a_items = [ p for p in posn_items if p[1] > target ]
        ### incorporate d_items in case no a_items?
        if lower_a_items:
            max_lower = max(lower_a_items)
            if upper_a_items:
                min_upper = min(upper_a_items)
                num = interpolated_word_number(max_lower[0], max_lower[1],
                                               target,
                                               min_upper[0], min_upper[1])
            else:
                num = extrapolated_word_number(max_lower[0], max_lower[1],
                                               target)
        elif upper_a_items:
            min_upper = min(upper_a_items)
            num = extrapolated_word_number(min_upper[0], min_upper[1], target)
        else:
            num = estimated_word_number(row, col)
        return bisect_left_max(anums, num), bisect_left_max(dnums, num)


# ---------- Misc. puzzle utilities ---------- #

# Record a summary of current action for undo/redo messages.

    def save_action_string(self, action, num=0, dir=None):
        if num:
            action = action + (' %s-%s' % (num, dir_text[dir]))
        self.eph.action_string = action

# For each direction, determine number of words placed on a grid and number
# of words in listbox.

    def current_word_count(self, dir):
        return len(self.perm.grid_id[dir]), self.gui.wordbox[dir].size()

# Calculate current puzzle size based on row and column extent seen
# on main grid.  For text form, return width, height in a string.
# For numeric form, return first row, column and width, height.

    def current_puzzle_size(self, text_form=1):
        posns = self.perm.posns[0]
        if not posns[0] and not posns[1]:
            if text_form: return '0 x 0'
            else:         return (0, 0, 0, 0)
        across = self.perm.words[0]
        down   = self.perm.words[1]
        first_rows, first_columns = [], []
        last_rows, last_columns   = [], []    # one past last
        for w in posns[0].items():
            row = w[1][0]
            first_rows.append(row)
            last_rows.append(row + 1)
            col = w[1][1]
            first_columns.append(col)
            last_columns.append(col + len(across[w[0]]))
        for w in posns[1].items():
            row = w[1][0]
            first_rows.append(row)
            last_rows.append(row + len(down[w[0]]))
            col = w[1][1]
            first_columns.append(col)
            last_columns.append(col + 1)
        first_row = min(first_rows)
        first_col = min(first_columns)
        width  = max(last_columns) - first_col
        height = max(last_rows) - first_row
        if text_form:
            return '%d x %d' % (width, height)
        else:
            return (first_row, first_col, width, height)


    def new_puzzle_file(self):
        self.gui.status_line['text'] = ''
        self.gui.puzzle_size['text'] = '0 x 0'
        self.gui.solving_time['text'] = '00:00'
        self.master.title('%s -- Diagnil' % new_puz_file)
        self.eph.save_time_id = \
            update_msg_widget(self.gui.save_time_msg, 'Not yet saved',
                              self.eph.save_time_id)

    def puz_file_name(self):
        return os.path.splitext(os.path.basename(self.temp.puz_file))[0]

    def update_window_title(self):
        if self.temp.puz_defn:
            size_field = ' (%dx%d)' % (self.temp.puz_defn.width,
                                       self.temp.puz_defn.height)
        else:
            size_field = ''
        puz_name = self.puz_file_name() or new_puz_file
        root.title('%s%s -- Diagnil' % (puz_name, size_field))

# The timer ticks off the seconds since solving began.  Better accuracy
# is achieved by saving the real time and setting the timeout according
# to the actual time needed to reach the next tick.  If a large delay is
# encountered, timing will adjust to get back on track.

    def count_tick(self):
        if self.sess.quitting: return
        current_time = time.time()
        elapsed = current_time - self.eph.last_tick
        if elapsed >= 2.0:
            sec_to_advance = elapsed // 1.0
            debug_log("*** Long tick: %s ***" % elapsed)
        else:
            sec_to_advance = 1.0
        # advance by an integral number of seconds
        self.eph.last_tick += sec_to_advance
        excess = elapsed - sec_to_advance
        timeout = int(1000 * (1.0 - excess))
        self.temp.solv_time += sec_to_advance
        self.gui.solving_time['text'] = timer_display(self.temp.solv_time)
        self.eph.timer_id = self.master.after(timeout, self.count_tick)

    def start_timer(self):
        self.master.after_cancel(self.eph.timer_id)
        self.eph.timer_id = self.master.after(1000, self.count_tick)
        self.eph.last_tick = time.time()

    def stop_timer(self):
        self.master.after_cancel(self.eph.timer_id)

    def restart_timer(self):
        if not self.perm.final:
            self.start_timer()

# Update the list of recently opened files.  The settings are changed and
# the submenu is recreated.

    def update_recent_list(self, puz_file):
        recent = app_recent['open_files']
        recent.insert(0, puz_file)
        names = [ os.path.splitext(os.path.basename(f))[0] for f in recent ]
        try:
            prev = names[1:].index(names[0])
            del recent[prev+1]      # remove earlier duplicate
        except ValueError:
            pass
        if len(recent) > num_recent:
            del recent[-1]
        app_recent['open_files'] = recent
        update_submenu(self.master.menubar_items,
                       self.master.menu_tags['Open Recent'],
                       self.make_recent_list())

    def set_menu_item_state(self, new_state, *items):
        for name in items:
            update_menu_item(self.master.menubar_items,
                             self.master.menu_tags[name],
                             state=new_state)

        
# ---------- Edit user preferences ---------- #

    def display_preference_dialog(self, parent):
        anchored_widget(parent, Label, padx=10, text='General Settings:')
        sett_fr = Frame(parent)

        ident_fn = lambda v: v
        var_dict = {}
        convert_dict = {}
        for name, parent, descrip in \
            (('infer_nums', None,
              'Display word number estimates on grid'),
             ('key_navigation', None,
              'Enable keystroke-based grid navigation'),
             ('auto_complete', None,
              'Automatically check for puzzle completion (clueful mode)'),
             ('upper_case', None,
              'Use upper case in word list panels'),
             ('wide_layout', None,
              'Use wide window layout with long word list panels'),
             ('show_boundary', None,
              'Show size-bounded puzzle region on startup'),
             ('apply_symmetry', 'show_boundary',
              'Show black squares implied by symmetry (when size is used):'),
             ) :
            var = BooleanVar()
            chfr = Frame(sett_fr)
            chkb = Checkbutton(chfr, variable=var, text=descrip)
            chkb.pack(side=LEFT)
            var.set(app_prefs_user[name])
            chfr.pack(padx=5, pady=5, fill=X)
            var_dict[name] = (var, ident_fn, chkb, [])
            if parent: var_dict[parent][3].append((name, chkb))
            chkb['command'] = \
                lambda name=name: update_dependents(name, var_dict)

        var = StringVar()
        for radio_list in ((('Rotational', 'rot'),
                            ('Horizontal', 'horiz'),
                            ('Vertical', 'vert')),
                           (('Diagonal, UL-LR', 'ul-lr'),
                            ('Diagonal, UR-LL', 'ur-ll'))):
            radio_fr = Frame(sett_fr)
            for label, key in radio_list:
                radbut = Radiobutton(radio_fr, variable=var,
                                     value=key, text=label)
                radbut.pack(side=LEFT, padx=5)
                var_dict['apply_symmetry'][3].append((None, radbut))
            radio_fr.pack(padx=40, pady=2, fill=X)
        var.set(app_prefs_user['symmetry_type'])
        var_dict['symmetry_type'] = (var, ident_fn, None, [])
        convert_dict['symmetry_type'] = \
            lambda vals: validate_symmetry_type(vals['symmetry_type'],
                                                vals['puzzle_width'],
                                                vals['puzzle_height'])
        Frame(sett_fr).pack(pady=5)

        size_fr = Frame(sett_fr)
        label = Label(size_fr, text='Default puzzle size on startup:')
        label.pack(side=LEFT)
        var_dict['show_boundary'][3].append((None, label))
        size_fr.pack(padx=5, pady=5, fill=X)

        size_fr = Frame(sett_fr)
        pref_wid = app_prefs_user['puzzle_width']
        pref_ht  = app_prefs_user['puzzle_height']

        var = IntVar()
        var.set(0)                  # 0 is code for custom size
        def spin_set(spin, n, enable=0):
            if enable: spin['state'] = NORMAL
            spin.delete(0, END)
            spin.insert(0, n)
            if enable: spin['state'] = DISABLED
        def update_custom(n):
            spin_set(var_dict['puzzle_width'][0], n, 1)
            spin_set(var_dict['puzzle_height'][0], n, 1)
            update_dependents('custom', var_dict)
        for v in (15, 17, 19, 21):
            radbut = Radiobutton(size_fr, variable=var, value=v,
                                 command=lambda n=v: update_custom(n),
                                 text='%d x %d' % (v,v))
            radbut.pack(side=LEFT, padx=5)
            var_dict['show_boundary'][3].append((None, radbut))
            if (pref_wid, pref_ht) == (v, v):
                var.set(v)
        size_fr.pack(padx=40, pady=2, fill=X)

        size_fr = Frame(sett_fr)
        radbut = Radiobutton(
                    size_fr, variable=var, value=0, text='Custom:   ',
                    command=lambda : update_dependents('custom', var_dict))
        radbut.pack(side=LEFT, padx=5)
        var_dict['show_boundary'][3].append(('custom', radbut))
        # if any predefined square size is selected, disable the custom option
        var_dict['custom'] = (var, lambda v: v == 0, radbut, [])

        size = grid_size[0]
        for name, cur_val, descrip in \
                zip(('puzzle_width', 'puzzle_height'),
                    (pref_wid, pref_ht),
                    ('Width:', 'Height:')):
            label = Label(size_fr, text=descrip)
            label.pack(side=LEFT)
            var_dict['custom'][3].append((None, label))
            var = Spinbox(size_fr, from_=3, to_=size, justify=CENTER, width=4)
            spin_set(var, min(cur_val, size))
            var.pack(side=LEFT, padx=6)
            Frame(size_fr).pack(side=LEFT, padx=5)
            var_dict[name] = (var, ident_fn, None, [])
            var_dict['custom'][3].append((None, var))
            convert_dict[name] = \
                lambda vals, name=name: validate_puzzle_size(vals[name], size)

        size_fr.pack(padx=40, pady=2, fill=X)
        Frame(sett_fr).pack(pady=5)
        update_dependents('show_boundary', var_dict)

        for name, descrip, values in \
            (('max_undo', 'Maximum number of undo steps:  ', (5, 10, 20, 40)),
             ('popup_delay', 'Pop-up delay (tenths of a second):  ' ,
              (2, 4, 6, 8))) :
            var = IntVar()
            fr = Frame(sett_fr)
            Label(fr, text=descrip).pack(side=LEFT)
            for v in values:
                Radiobutton(fr, variable=var, value=v,
                            text=str(v)).pack(side=LEFT, padx=5)
            var.set(app_prefs_user[name])
            fr.pack(padx=5, pady=5, fill=X)
            var_dict[name] = (var, ident_fn, None, [])
        Frame(sett_fr).pack(pady=5)

        ent_fr = Frame(sett_fr)
        Label(ent_fr,
              text='Folder for storing puzzle files:  ').pack(side=LEFT)
        save_var = StringVar()
        dir_ent = SunkenEntry(ent_fr, width=20, background=text_bg_color,
                              textvariable=save_var)
        dir_ent.pack(side=LEFT)
        def br_direc():
            direc = askdirectory(
                        title='Choose puzzle folder',
                        initialdir=self.sess.initial_dir)
            if direc:
                dir_ent.delete(0, END)
                dir_ent.insert(0, direc)
        br_cmd = EventHandler('Browse puzzle direc', br_direc)
        if using_ttk or using_tile:
            browse = Button(ent_fr, text='Browse', width=8, command=br_cmd)
        else:
            browse = ThinButton(ent_fr, text='Browse', command=br_cmd,
                                min_width=6)
        browse.pack(side=LEFT, padx=5)
        save_var.set(app_prefs_user['puzzle_folder'])
        ent_fr.pack(padx=5, pady=5, fill=X)
        var_dict['puzzle_folder'] = (save_var, ident_fn, None, [])
        sett_fr.pack(padx=10, pady=5, fill=X)

        def update_preference_values():
            val_dict = {}
            # build value dict by retrieving values from Tk widget variables
            for name, var in var_dict.items():
                val_dict[name] = var[0].get()
            # first remove pseudo-values
            del val_dict['custom']
            # convert all values first so exceptions won't lead to
            # partial state changes
            cvals = [ (name, convert(val_dict))
                      for name, convert in convert_dict.items() ]   # => excep
            for name, val in cvals:
                app_prefs_user[name] = val
                del val_dict[name]
            for name, val in val_dict.items():
                app_prefs_user[name] = val
        return update_preference_values


# ---------- Error-checking application methods ---------- #

# In clueful mode, a word number has to be in the puzzle definition.

    def check_non_puz_defn_num(self, dir, num):
        if self.temp.puz_defn and \
           num not in self.temp.puz_defn.nums[dir]:
            user_dialog(showerror, *error_msg_sub('extra_word_number',
                                                  (num, dir_text[dir])))
            raise UserError

# Word placement is checked for possible conflicts with other items on the
# grid.  First a check for grid overflow is performed.

    def check_grid_overflow(self, dir, word, id, row, col):
        if not (0 <= row < grid_size[id]) or not (0 <= col < grid_size[id]) \
           or not (0 <= row*dir + col*(1-dir) <= grid_size[id] - len(word)):
            self.paint_word_pre(id, dir, word, row, col,
                                ('error',), error_color, error_box_width)
            self.raise_error_scroll(id, row, col,
                                    *error_msg_sub('out_of_bounds', word))

# Then the cell for every letter is checked to see if it is already
# occupied by a block or a word in the same direction.  Crossing word
# contents are allowed, but a check is made elsewhere for clashing letters.

    def check_conflict(self, dir, word, num, id, row, col):
        if not (0 <= row < grid_size[id]) or not (0 <= col < grid_size[id]) \
           or not (0 <= row*dir + col*(1-dir) <= grid_size[id] - len(word)):
            self.paint_word_pre(id, dir, word, row, col,
                                ('error',), error_color, error_box_width)
            self.raise_error_scroll(id, row, col,
                                    *error_msg_sub('out_of_bounds', word))
        cells = self.aux.cells[id]
        conflict = 0
        for r,c in generate_cells(dir, len(word), row, col):
            cell = cells[r][c]
            if cell[dir] or cell[2]: conflict = 1
        for r,c in end_blocks(grid_size[id], dir, len(word), row, col):
            if cells[r][c][1-dir]: conflict = 1
        if conflict:
            self.paint_word_pre(id, dir, word, row, col,
                                ('error',), error_color, error_box_width, 1)
            self.raise_error_scroll(id, r, c,
                                    *error_msg_sub('place_conflict',
                                                   (num, word)))

# Check if the letters of word cross any end blocks of crossing words.
# If so, ask for confirmation to extend crossing words with letters
# from new word.  Return a list of (num, word, row, col) tuples for
# words to be extended.  If user declines, raise UserError.
# Otherwise, return empty list.

    def cross_extensions(self, dir, word, id, row, col):
        cells = self.aux.cells[id]
        cross_words = self.perm.words[1-dir]
        cross_posns = self.perm.posns[id][1-dir]
        ext_list = []
        for r,c in generate_cells(dir, len(word), row, col):
            if cells[r][c][2]:   # crossing cell has a block
                if dir:          # crossing words are across
                    if c > 0 and cells[r][c-1][0]:   # crossing word found
                        if cells[r][c+1][0] or cells[r][c+1][1]:
                            return []   # sorry, cell for new block is occupied
                        ext_num = cells[r][c-1][0][0]
                        ext_word = cross_words[ext_num] + word[r - row]
                        posn = cross_posns[ext_num]
                        ext_list.append((ext_num, ext_word, posn[0], posn[1]))
                else:            # crossing words are down
                    if r > 0 and cells[r-1][c][1]:
                        if cells[r+1][c][0] or cells[r+1][c][1]:
                            return []   # sorry, cell for new block is occupied
                        ext_num = cells[r-1][c][1][0]
                        ext_word = cross_words[ext_num] + word[c - col]
                        posn = cross_posns[ext_num]
                        ext_list.append((ext_num, ext_word, posn[0], posn[1]))
        ext_nums = [ tup[0] for tup in ext_list ]
        if ext_nums:
            self.paint_word_pre(id, dir, word, row, col,
                                ('error',), error_color, error_box_width)
            title, message = \
                   error_msg_sub('extend_crossing',
                                 (dir_text[dir], word, dir_text[1-dir],
                                  gen_list_text(ext_nums)))
            extend = self.raise_error_scroll(id, row, col, title, message,
                                             askokcancel)
            self.gui.grids[id].delete('error')   # clean up highlighting
            if not extend: raise UserError
        return ext_list

# The first letters (head cells) of words are subject to two constraints.
# (1) If both across and down words exist for the same word number, they
# must be placed in the same cell.  (2) If across and down words both start
# at the same cell, they must have the same word number.

    def head_cell_mismatch(self, dir, num, id, row, col):
        posns = self.perm.posns[id][1-dir]
        cell = self.aux.cells[id][row][col][1-dir]
        posn = posns.get(num)
        if posn and posn != (row,col):
            self.raise_error_scroll(id, row, col,
                                    *error_msg_sub('head_cell_split',
                                                   (num, dir_text[dir],
                                                    num, dir_text[1-dir])))
        if cell and cell[0] != num and posns[cell[0]] == (row,col):
            self.raise_error_scroll(id, row, col,
                                    *error_msg_sub('head_cell_clash',
                                                   (num, dir_text[dir],
                                                    cell[0], dir_text[1-dir])))

# Words should be placed in order on the grid, i.e., they should maintain
# cell(word[i]) <= (row,col) <= cell(word[i+1]).

    def word_out_of_order(self, num, id, row, col):
        for dir in (0,1):
            num_list = self.perm.nums[dir]
            posns = self.perm.posns[id][dir]
            grid_id = self.perm.grid_id[dir]
            num_list = [ n for n in num_list if grid_id.get(n) == id ]
            index = bisect_left(num_list, num)
            if index > 0 and posns[num_list[index-1]] > (row,col) or \
               index < len(num_list) and posns[num_list[index]] < (row,col):
                self.eph.warnings['out-of-order'] = 1

# If num already exists and its word differs from new one being inserted,
# issue a warning after overwriting.
# Special case: placeholder chars match any other chars.

    def word_overwrite_check(self, dir, num, word):
        try:
            old_word = self.perm.words[dir][num]
            mismatch = 1
            if len(word) == len(old_word):
                for a,b in zip(word, old_word):
                    if b == placeholder: continue
                    if a != b: break
                else:
                    mismatch = 0
            if mismatch:
                self.eph.warnings['unconfirmed_overwrite'] = \
                    (old_word, num, dir_text[dir], word, old_word)
        except KeyError:
            pass   # num not found

# Words should be unique within listboxes (for normally constructed puzzles).
# We don't insist on it, but issue a warning on detection.

    def duplicate_word_check(self, new_dir, new_num, word):
        if '?' in word: return    # one or more ? chars disqualify a match
        if null_word_symb == word: return    # so does null word
        matches = []
        for dir in (0,1):
            word_list = self.perm.words[dir]
            matches.extend([ (p[0], dir) for p in word_list.items()
                             if p[1] == word and
                                (dir != new_dir or p[0] != new_num) ])
        if matches:
            # args to warning message: (word, num, dir)
            # only first duplication cited; multiple cases should be rare
            self.eph.warnings['duplicate_word'] = \
                 (word, matches[0][0], dir_text[matches[0][1]])

# On errors, try to make relevant cell(s) easily visible by scrolling
# them into view if currently off-screen, then restoring scroll position.

    def raise_error_scroll(self, id, row, col, title, message,
                           show_proc=showerror):
        grid = self.gui.grids[id]
        x0, y0 = grid.canvasx(0), grid.canvasy(0)
        x1, y1 = x0 + grid.winfo_width(), y0 + grid.winfo_height()
        if not (x0 <= col*cell_size < x1 and y0 <= row*cell_size < y1):
            self.gui.scroll_grid[id](row - 4, col - 4)
            result = user_dialog(show_proc, title, message)
            self.gui.scroll_grid[id](y0//cell_size, x0//cell_size)
        else:
            result = user_dialog(show_proc, title, message)
        if show_proc is showerror: raise UserError
        return result

# Grid cursors are selected by index value 0..2.  0, 1 are for across, down
# directions.  2 is used after a puzzle is finalized.

    if on_win:   ### colored cursors fail under Windows
        def set_grid_cursors(self, dir, cursor=None):
            # if cursor present, dir is ignored
            if not cursor:
                cursor = grid_cursors[dir]
            for id in range(num_grids):
                self.gui.grids[id].configure(cursor=cursor)
    else:
        def set_grid_cursors(self, dir, cursor=None):
            # if cursor present, dir is ignored
            if not cursor:
                cursor = grid_cursors[dir]
            for id in range(num_grids):
                self.gui.grids[id].configure(cursor=(cursor, cursor_color))

# Main variables need to maintain the following invariant, which is
# checked after every action if enabled by check_assertions flag.
# The assertion is not too thorough; basically it ensures
# that data items in perm and aux aren't missing.  It also does a
# reverse check that words pointed to by aux.cells exist in perm.
# This checking is still less than full consistency.

    def state_invariant(self):
        for i, perm in enumerate(self.temp.undo_state):
            if isinstance(perm[0], PermState): continue
            return 'Undo state value at position %d is "%s".' % (i, perm)
        for dir in (0,1):
            nums = self.perm.nums[dir]
            for i in range(len(nums) - 1):
                num = nums[i]
                if num >= nums[i+1]:
                    return 'List out of order: dir = %d, num = %d\n\n' \
                           % (dir, num)
                if not self.perm.words[dir].has_key(num):
                    return 'Missing word string: dir = %d, num = %d\n\n' \
                           % (dir, num)
                try:
                    id = self.perm.grid_id[dir][num]   # examine gridded words
                    try:
                        row,col = self.perm.posns[id][dir][num]
                        if not self.aux.cells[id][row][col][dir]:
                            return 'Missing cell data: dir = %d, num = %d,' \
                                   'id = %d\n\n' % (dir, num, id)
                    except KeyError:
                        return 'Missing position for gridded word: ' \
                               'dir = %d, num = %d, id = %d\n\n' \
                               % (dir, num, id)
                except KeyError:    # ignore ungridded words
                    pass
        for id in range(num_grids):
            for row,col in self.perm.blocks[id]:
                if not self.aux.cells[id][row][col][2]:
                    return 'Missing block data: dir = %d, id = %d,' \
                           'row = %d, col = %d\n\n' % (dir, id, row, col)
        for id in range(num_grids):
            cells = self.aux.cells[id]
            for dir in (0,1):
                nums  = self.perm.nums[dir]
                for row in range(grid_size[id]):
                    for col in range(grid_size[id]):
                        cell = cells[row][col][dir]
                        if cell:
                            if cell[0] not in nums:
                                return 'Cell (%d,%d)[%d] of grid %d points ' \
                                       'to word %d, which does not exist.' \
                                       % (row,col,dir,id,cell[0])
                            if cells[row][col][2]:
                                return 'Cell (%d,%d)[%d] of grid %d clashes ' \
                                       'with a block.' % (row,col,dir,id)
                                
        return ''    # no problems detected
