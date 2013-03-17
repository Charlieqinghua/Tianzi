#  Diagnil: Diagramless Crossword Assistant        Version 3.0
#      A utility for solving diagramless puzzles interactively
#
#  Copyright (c) 2003-2012, Ben Di Vito.  <bdivito@cox.net>
#
#  This is open source software, distributed under a BSD-style license.
#  See the accompanying file 'License' for details.
#

from diag_globals   import *
from textwrap       import wrap
from diag_multilistbox import MultiListbox


# ---------- Word/answer parsing ---------- #

# A regular expression match is used to split a text entry into its number
# and word fields.  Basic word text must match <digit>* <white>* <word-spec>,
# where <word-spec> can be <alpha>+ (with placeholder chars allowed)
# or <placeholder> <white>* <digit>+.  Word spec can also contain wildcards
# interspersed among the letters ('*' is wildcard char).
# Starting and trailing blanks are ignored.  Three special cases
# are allowed: word only, number only, and empty/blank string.
# These cases represent shortcuts handled by the entry procedures.
# Word fields (without the '*' wildcards) may consist of comma-separated
# word lists.
# Returns (num, wild, word), with num = -1 if number missing,
# wild = 1 if wildcards present, in which case word is a list of strings
# (each a word fragment or '*').

_word_chars        = '[a-zA-Z%s]+' % placeholder
_word_alt_chars    = '[a-zA-Z,%s]+' % placeholder
_word_num_only     = re.compile('\A(\d+)\Z')
_word_num_plus     = re.compile('\A(\d+)\s*(.*)\Z')
_word_only_spec    = re.compile('\A(%s)\Z' % _word_alt_chars)
_wild_word_chars   = re.compile('\A(%s|\*)+\Z' % _word_chars)
_wild_word_frags   = re.compile('(%s|\*)\s*' % _word_chars)
_placeholder_spec  = re.compile('\A\%s\s*(\d+)\Z' % placeholder)  # ? <num>

def parse_word_entry(txt, show_error=1):
    txt = string.strip(txt)
    if txt == '':             # number and word both required
        return -1, 0, ''
    fields = _word_num_plus.split(txt)   # do this check first to find num
    if len(fields) == 4:
        num, rest = fields[1:3]
        fields = _word_only_spec.split(rest)
        if len(fields) == 3: return int(num), 0, fields[1]
        fields = _wild_word_chars.split(rest)   # word with wildcards
        if len(fields) >= 3:
            return int(num), 1, [x for x in _wild_word_frags.split(rest) if x]
        fields = _placeholder_spec.split(rest)
        if len(fields) == 3: return int(num), 0, placeholder * int(fields[1])

    fields = _word_only_spec.split(txt)  # check for word without num
    if len(fields) == 3:
        return -1, 0, fields[1]  # num = -1 to indicate inference required
    fields = _wild_word_chars.split(txt)   # word with wildcards
    if len(fields) >= 3:
        return -1, 1, [x for x in _wild_word_frags.split(txt) if x]

    fields = _placeholder_spec.split(txt) # check for placeholder only
    if len(fields) == 3:
        return -1, 0, placeholder * int(fields[1])
    fields = _word_num_only.split(txt)          # check for number only
    if len(fields) == 3:
        return int(fields[1]), 0, ''  # word = '' to indicate lookup required
    # all other cases generate error (UserError)
    if show_error:
        raise_error(*error_msg_sub('invalid_word_entry', txt))
    else:
        raise UserError


def parse_word(txt, show_error=1):
    num, wild, word = parse_word_entry(txt, show_error)               ###
    if num == 0:
        if show_error:
            raise_error(*error_messages['zero_word_number'])          ###
        else:
            raise UserError
    if app_prefs['upper_case']: trans = lambda s: s.upper()
    else:                       trans = lambda s: s.lower()
    if isinstance(word, str): word = trans(word)
    else:                     word = [ trans(w) for w in word ]
    return num, wild, word

# Check for number plus rest of word entry string.  If number exists,
# return number, rest; otherwise, return -1, ''.

def parse_number(txt):
    txt = string.strip(txt)
    if txt == '':             # number required
        return -1, ''
    fields = _word_num_plus.split(txt)
    if len(fields) == 4:
        num, rest = fields[1:3]
        return int(num), rest
    else:
        return -1, ''

_grid_indicators = re.compile('-|\+|#')

def parse_wordlist_item(item):
    return parse_word(_grid_indicators.sub('', item))  # strip -+# first

def placeholder_congruent(x, y):
    if placeholder in x or placeholder in y:
        return all(map(lambda a, b:
                           a == b or a == placeholder or b == placeholder,
                       x, y))
    else:
        return x == y


# ---------- Grid cell painting ---------- #

# Individual cells are displayed on the canvas with optional number in the
# upper left corner.  If a letter clash is indicated, a small red dot is
# added to the lower right corner and the text argument can be a pair of
# letters, both of which are displayed (in a smaller font).  Three tags are
# used: word tag, cell tag, letter tag, e.g., ('a23', 'a23:15.48', 'letter').

def paint_cell(canv, i, j, txt, tag, num=None, clash=None, color='black'):
    wtags = (tag, letter_cell_tag(tag, i, j), 'letter')
    if isinstance(txt, tuple):
        aletter, dletter = txt
        canv.create_text(j*cell_size+clash_offsets[0],
                         i*cell_size+clash_offsets[1],
                         text=string.upper(aletter), tags=wtags,
                         font=clash_font, fill=color)
        canv.create_text(j*cell_size+clash_offsets[2],
                         i*cell_size+clash_offsets[3],
                         text=string.upper(dletter), tags=wtags,
                         font=clash_font, fill=color)
    else:
        canv.create_text(j*cell_size+cell_offset, i*cell_size+cell_offset,
                         text=string.upper(txt), tags=wtags, font=grid_font,
                         fill=color)
    if num:
        canv.create_text(j*cell_size+2, i*cell_size+5, tags=wtags, anchor=W,
                         text=("%d" % num), font=num_font, fill=num_color)
    # consider adding a slot to cell to save canvas id rather than using tags
    if clash:
        x,y = (j+1)*cell_size - 4, (i+1)*cell_size - 4
        canv.create_oval(x-2, y-2, x+2, y+2,
                         tags=(clash_dot_tag(i,j),'letter'),
                         outline=clash_color, fill=clash_color)

def letter_cell_tag(tag, row, col):
    return '%s:%d.%d' % (tag, row, col)     # tag of form <a/dnum>:row.col

def clash_dot_tag(row, col):
    return 'c:%d.%d' % (row, col)           # tag of form c:row.col

def paint_cell_temp(canv, i, j, txt, wtags, bg, fg,
                    hide_placeholder=0, below=0, over_block=0):
    x, y = j*cell_size, i*cell_size
    # Hide existing cell contents before overlaying temporary letter.
    rect = canv.create_rectangle(x+1, y+1, x+cell_size, y+cell_size,
                                 tags=wtags, width=0, fill=bg)
    if below:
        canv.tag_lower(rect, below)
    canv.create_text(x+cell_offset, y+cell_offset, text=string.upper(txt),
                     tags=wtags, font=grid_font, fill=fg)
    if over_block:
        paint_cell_border(canv, i, j, wtags)

def paint_cell_border(canv, i, j, tags=('m_aids',)):
    x, y = j*cell_size, i*cell_size
    canv.create_rectangle(x+2, y+2, x+cell_size-1, y+cell_size-1,
                          tags=tags, width=2, outline='red')

def paint_missing_head(canv, dir, i, j, tags=('error',)):
    paint_cell_border(canv, i, j, tags=tags)
    paint_triangle_pointer(canv, dir, i, j, tags)

def paint_triangle_pointer(canv, dir, i, j, tags, color='red'):
    x, y = j*cell_size, i*cell_size
    if dir:
        canv.create_polygon(x+3, y+3, x+half_cell_size+1, y+8,
                            x+cell_size-3, y+3,
                            outline='', fill=color, tags=tags)
    else:
        canv.create_polygon(x+3, y+3, x+8, y+half_cell_size+1,
                            x+3, y+cell_size-3,
                            outline='', fill=color, tags=tags)

# Active cursors use dir of 0 or 1; inactive ones have dir = 2.

def paint_key_cursor(canv, dir, i, j, below):
    tag = 'key_cursor'
    canv.delete(tag)
    x, y = j*cell_size, i*cell_size
    if dir < 2:
        if dir:
            coords = (x+1, y+1,
                      x+1, y+half_cell_size+5, 
                      x+half_cell_size+1, y+cell_size,
                      x+cell_size, y+half_cell_size+5,
                      x+cell_size, y+1)
        else:
            coords = (x+1, y+1,
                      x+half_cell_size+5, y+1,
                      x+cell_size, y+half_cell_size+1,
                      x+half_cell_size+5, y+cell_size,
                      x+1, y+cell_size)
        cursor = canv.create_polygon(*coords, outline='',
                                      fill=key_cursor_color, tags=(tag,))
    else:
        cursor = canv.create_rectangle(
                     x+1, y+1, x+cell_size, y+cell_size,
                     outline='', fill=dim_cursor_color, tags=(tag,))
    canv.tag_lower(cursor, below)
    return cursor

# Paint inferred number above cell or to its left to make it clearly
# visible.  Partially hide contents of adjacent block temporarily.
# Filter out cases where word numbers are already displayed;
# argument 'force' suppresses this filtering.
# Arg 'interior' has conditions (not leftmost column, not top row).

def paint_inferred_number(canv, cells, dir, i, j, wtags,
                          num, exists, interior, force=0):
    if not force:
        this_cell = cells[i][j]
        # check if have head cell of across word or down word
        if (j == 0 or not cells[i][j-1][0]) and this_cell[0] or \
           (i == 0 or not cells[i-1][j][1]) and this_cell[1] :
            return    # found head cell => already numbered
    right = 0
    if dir:
        if interior[dir]: i -= 1
    else:
        if interior[dir]: j -= 1; right = 1
    if exists:
        color = num_exists_color
    else:
        color = inferred_color
    if num == 0: num = no_num_symbol
    x, y = j * cell_size, i * cell_size
    # if cell (i,j) contains a block, obscure background
    # before overwriting with number
    if cells[i][j][2]:
        canv.create_rectangle(x+1, y+half_cell_size, x+cell_size, y+cell_size,
                              tags=wtags, width=0, fill=word_bg_color)
    if right:
        canv.create_text(x+cell_size-2, y+cell_size-5, tags=wtags, anchor=E,
                         text=('%s' % num), font=num_font, fill=color)
    else:
        canv.create_text(x+2, y+cell_size-5, tags=wtags, anchor=W,
                         text=('%s' % num), font=num_font, fill=color)

def paint_bounding_box(canv, dir, row, col, wlen, tags, color,
                       width, extent=1):
    canv.create_rectangle(col*cell_size+1, row*cell_size+1,
                          (col + dir*extent + (1-dir)*wlen) * cell_size,
                          (row + (1-dir)*extent + dir*wlen) * cell_size,
                          tags=tags, width=width, outline=color)

# Following items are created with tag 'aids' or 'marker' for easy removal.

def paint_rect(canv, i1, j1, i2, j2):    # for region bounding box
    x1,y1 = j1*cell_size, i1*cell_size
    x2,y2 = j2*cell_size, i2*cell_size
    canv.create_rectangle(x1+2, y1+2, x2+cell_size-2, y2+cell_size-2,
                          tags=('aids',), width=3, outline=region_color)

def paint_diagonal_boundary(canv, i1, j1, i2, j2, isize):   # 3 line segments
    xy = [ x * cell_size + half_cell_size for x in 
           ( j1, 0, j1, i1, j2, i2, j2, 0 ) ]
    xy[1] = 0
    xy[7] = isize * cell_size
    canv.create_line(xy[0], xy[1], xy[2], xy[3], xy[4], xy[5], xy[6], xy[7],
                     tags=('aids',), width=4, fill=region_color)

def paint_cell_marker(canv, i, j):  # to mark reference cell during movement
    x,y = j*cell_size, i*cell_size
    canv.create_rectangle(x+8, y+8, x+cell_size-8, y+cell_size-8,
                          tags=('marker',), width=3, outline=marker_color,
                          fill=marker_color)


# ---------- Misc. utility procedures ---------- #
    
def generate_cells(dir, n, row, col): # Iterate over cells in given direction.
    for i in range(n):
        yield row + i*dir, col + i*(1-dir)

def end_blocks(size, dir, word_len, row, col): # Positions of up to two blocks
    r,c = row - dir, col - (1-dir)
    if r >= 0 and c >= 0: blocks = [(r,c)]
    else:                 blocks = []
    r,c = row + word_len*dir, col + word_len*(1-dir)
    if r < size and c < size: blocks.append((r,c))
    return blocks

def validate_puzzle_size(raw_dim, max_size):
    def reject_size(dim):
        user_dialog(showerror,
                    *error_msg_sub('bad_puzzle_size', (dim, max_size)))
        raise FalseStart
    try:
        dim = int(raw_dim)
    except ValueError:
        reject_size(raw_dim)
    if not (3 <= dim  <= max_size):
        reject_size(dim)
    return dim

def validate_symmetry_type(symm_type, width, height):
    if symm_type in ('ul-lr', 'ur-ll') and width != height:
        user_dialog(showerror, *error_messages['size_not_square'])
        raise FalseStart
    return symm_type


# Estimate word number on a grid according to cell location.  Assumes
# a word-number growth curve.  Both absolute and relative versions
# are available.  Extrapolated estimate is based on a reference cell having
# a known word number.  Interpolated estimate lies between lower and
# upper reference cells.

def estimated_word_number(row, col):
    return cum_word_nums_curve[row] + \
           int(round(word_nums_curve[row] * col / 20.0))

def extrapolated_word_number(num, ref, target):
    # estimates number relative to number at reference cell; works for
    # both upper and lower directions;
    col_offsets = [ int(round(word_nums_curve[r] * c / 20.0))
                    for r, c in (ref, target) ]
    row_delta = cum_word_nums_curve[target[0]] - cum_word_nums_curve[ref[0]]
    return num + row_delta + col_offsets[1] - col_offsets[0]

def interpolated_word_number(lower_num, lower_posn, target,
                            upper_num, upper_posn):
    col_offsets = [ int(round(word_nums_curve[r] * c / 20.0))
                    for r, c in (lower_posn, target, upper_posn) ]
    lower_row_delta = cum_word_nums_curve[target[0]] - \
                      cum_word_nums_curve[lower_posn[0]]
    upper_row_delta = cum_word_nums_curve[upper_posn[0]] - \
                      cum_word_nums_curve[target[0]]
    lower_est = lower_num + (lower_row_delta + col_offsets[1] - col_offsets[0])
    upper_est = upper_num - (upper_row_delta + col_offsets[2] - col_offsets[1])
    # form the average even if lower > upper
    return (lower_est + upper_est) // 2

def select_actual_number(nums, lower, target, upper):
    # find an actual number (in the ordered number list) close to the target
    # but satisfying constraint lower <= num <= upper
    if not nums:
        return 0     # in practice, should always have some nums
    low_index, high_index = 0, len(nums) - 1
    index = min(bisect_left(nums, target), high_index)
    while low_index <= index <= high_index:
        candidate = nums[index]
        if lower <= candidate:
            if candidate <= upper:
                return candidate     # acceptable number found
            else:
                index -= 1
                high_index = index
        else:
            index += 1
            low_index = index
    return 0             # no feasible number exists


# Raise UserError by first showing a dialog message.

def raise_error(title, message):
    user_dialog(showerror, title, message)
    raise UserError

# Extract title, error message and apply string substitution st.

def error_msg_sub(key, st):   ## st is a string tuple or single string
    title, message = error_messages[key]
    return title, message % st

# Generate string of form "a, b,...,g and h".

def gen_list_text(items):
    if not items: return ''
    text = '%s' % items[0]
    if len(items) > 2:
        for x in items[1:-1]: text += ', %s' % x
    if len(items) > 1: text += ' and %s' % items[-1]
    return text

# Apply binary search and limit index to last element (len - 1).
# Returns -1 when list is empty.

def bisect_left_max(vlist, value):
    index = bisect_left(vlist, value)
    return min(index, len(vlist) - 1)


# Convert number of seconds into string approximation (e.g., "3.2 days").

def approx_duration(duration):
    # thresholds are 0.95 * sec_per_unit
    if duration > 29979079:
        return '%s years' % two_digit_min(duration, 31556926.0)
    elif duration > 82080:
        return '%s days' % two_digit_min(duration, 86400.0)
    elif duration > 3420:
        return '%s hours' % two_digit_min(duration, 3600.0)
    else:
        return '%s minutes' % two_digit_min(duration, 60.0)

def two_digit_min(value, divisor):
    scaled = value / divisor
    if scaled < 10.0:
        return str(round(scaled, 1))
    else:
        return str(int(round(scaled)))

def timer_display(value):
    hours, min_sec = value // 3600, value % 3600
    minutes, seconds = min_sec // 60, min_sec % 60
    if hours > 0:
        return '%d:%02d:%02d' % (hours, minutes, seconds)
    else:
        return '%02d:%02d' % (minutes, seconds)

def mod_time_ago(mod_time):
    return '%s ago' % approx_duration(time.time() - mod_time)

def signum(x):
    if   x > 0: return 1
    elif x < 0: return -1
    return 0

gensym_num = 0
def gensym(base='dg_sym_'):
    global gensym_num
    gensym_num += 1
    return '%s%d' % (base, gensym_num)

    
# ---------- Tk/Tkinter widget utilities ---------- #


class SunkenEntry(Entry):
    def __init__(self, parent, **options):
        if not (using_ttk or using_tile):
            options = merged_options(options, relief=SUNKEN)
        Entry.__init__(self, parent, **options)

class ThinButton(Button):
    def __init__(self, parent, min_width=6, **options):
        if using_ttk or using_tile or on_aqua:
            widget_options = merged_options(options, default=DISABLED)
        else:
            widget_options = merged_options(options, pady=1, default=DISABLED)
        Button.__init__(self, parent, **widget_options)
        if 'width' not in options:
            self['width'] = max(min_width, button_width_estimate(self['text']))

class MediumButton(Button):
    def __init__(self, parent, min_width=6, **options):
        if using_ttk or using_tile or on_aqua:
            widget_options = merged_options(options, default=DISABLED)
        else:
            widget_options = merged_options(options, pady=3, default=DISABLED)
        Button.__init__(self, parent, **widget_options)
        if on_aqua and 'width' not in options:
            self['width'] = max(min_width, button_width_estimate(self['text']))

class FullButton(Button):
    def __init__(self, parent, min_width=6, **options):
        Button.__init__(self, parent, **options)
        if on_aqua and 'width' not in options:
            self['width'] = max(min_width, button_width_estimate(self['text']))


class ColoredFrame(Frame):
    def __init__(self, parent, borderwidth=1, bd=1, color='gray60', **options):
        bd = max(bd, borderwidth)
        Frame.__init__(self, parent, relief=FLAT, **options)
        # create four sides using specified width and color
        Frame(self, height=bd, relief=FLAT, bg=color).pack(fill=X)
        Frame(self, height=bd, relief=FLAT, bg=color).pack(side=BOTTOM, fill=X)
        Frame(self, width=bd, relief=FLAT, bg=color).pack(side=LEFT, fill=Y)
        Frame(self, width=bd, relief=FLAT, bg=color).pack(side=RIGHT, fill=Y)
        # remaining cavity is for packing children of Frame

class FlatScrollbar(Scrollbar):
    def __init__(self, parent, width=14, **options):
        if using_ttk or using_tile or on_aqua:
            Scrollbar.__init__(self, parent, **options)
        else:
            Scrollbar.__init__(self, parent, width=width, relief=FLAT,
                               bd=0, elementborderwidth=1, **options)

class FixedFrame(Frame):
    def __init__(self, parent, width=30, height=24, **options):
        frame_options = \
            merged_options(options, width=width, height=height)
        Frame.__init__(self, parent, **frame_options)
        self.pack_propagate(0)   # don't shrink

def anchored_widget(parent, widget_class, side=LEFT,
                    padx=0, pady=0, **options):
    fr = Frame(parent)
    widget_class(fr, **options).pack(side=side)
    fr.pack(padx=padx, pady=pady, fill=X, expand=YES)

def entry_widget(parent, **options):
    if using_ttk or using_tile:
        ent = Entry(parent, **options)
    elif on_aqua:
        ent = Entry(parent, highlightthickness=3,
                    background=text_bg_color, relief=SUNKEN, bd=2,
                    highlightcolor=highlight_color, **options)
    else:
        ent = Entry(parent, highlightthickness=2,
                    background=text_bg_color, relief=SUNKEN,
                    highlightcolor=highlight_color, **options)
        if not on_win:
            ent.configure(highlightbackground=master_bg)
    return ent


# Construct a scrolled text widget.  Returns containing frame, text widget.

def scrolled_text_widget(parent, width=40, height=24, barwidth=14,
                         horiz_scroll=0, tab_stops=(),
                         enter_focus=1, **text_options):
    fr = Frame(parent)
    if horiz_scroll: wrap_mode = NONE
    else:            wrap_mode = WORD
    text_widget_options = \
        merged_options(text_options, padx=5, pady=5,
                       wrap=wrap_mode, font=text_font,
                       width=width, height=height, highlightthickness=0,
                       state=NORMAL, background=text_bg_color, tabs=tab_stops)
    txt = Text(fr, **text_widget_options)
    scroll = FlatScrollbar(fr, command=txt.yview, width=barwidth)
    txt.configure(yscrollcommand=scroll.set)
    txt.grid(row=0, column=0, sticky='news')
    if enter_focus and not on_win:
        wrapped_bind(fr, '<Enter>', lambda event: txt.focus_set())
    fr.rowconfigure(0, weight=1, minsize=0)
    scroll.grid(row=0, column=1, sticky='ns')
    fr.columnconfigure(0, weight=1, minsize=0)
    fr.columnconfigure(1, weight=0, minsize=0)
    if horiz_scroll:
        hscroll = FlatScrollbar(fr, command=txt.xview, orient=HORIZONTAL,
                                width=barwidth)
        txt.configure(xscrollcommand=hscroll.set)
        hscroll.grid(row=1, column=0, sticky='ew')
        fr.rowconfigure(1, weight=0, minsize=0)
    return fr, txt

# Construct a scrolled listbox widget.  Returns containing frame, listbox.

def scrolled_listbox(parent, width=30, height=12, barwidth=14,
                     horiz_scroll=0, selectmode=SINGLE, **box_options):
    fr = Frame(parent)
    listbox_options = \
        merged_options(box_options, selectmode=selectmode, exportselection=0,
                       background=text_bg_color, height=height, width=width,
                       highlightthickness=0)
    listbox = Listbox(fr, **listbox_options)
    scrollbar = FlatScrollbar(fr, command=listbox.yview, width=barwidth)
    listbox.configure(yscrollcommand=scrollbar.set)
    listbox.grid(row=0, column=0, sticky='news')
    fr.rowconfigure(0, weight=1, minsize=0)
    scrollbar.grid(row=0, column=1, sticky='ns')
    fr.columnconfigure(0, weight=1, minsize=0)
    fr.columnconfigure(1, weight=0, minsize=0)
    if horiz_scroll:
        hscroll = FlatScrollbar(fr, command=listbox.xview, width=barwidth,
                                orient=HORIZONTAL)
        listbox.configure(xscrollcommand=hscroll.set)
        hscroll.grid(row=1, column=0, sticky='ew')
        fr.rowconfigure(1, weight=0, minsize=0)
    return fr, listbox

# Extended to several listbox columns.

def scrolled_multilistbox(parent, select_proc, height=12, barwidth=14,
                          **box_options):
    listbox_options = \
        merged_options(box_options, background=text_bg_color,
                       height=height, barwidth=barwidth,
                       highlightthickness=0) # , columns=columns)
    mlist =  MultiListbox(parent, FlatScrollbar,
                          select_action=select_proc, **listbox_options)
    return mlist

# Build a scrolling Tk listbox to hold word lists.

def word_list_multi(frame, height, select_proc, padx=0, pady=0,
                    **listbox_options):
    if on_win: num_wid = 3
    else:      num_wid = 2    # with small font, 3 is too wide
    mlist = scrolled_multilistbox(
                   frame, select_proc,   # proc already wrapped
                   height=height,
                   columns=(('', num_wid, 1, None, {}),
                            ('', 30 - num_wid, 1, 'wrap', {})),
                   selectbackground=listbox_sel_bg, **listbox_options)
    mlist.configure(relief='sunken', border=1)  ## border=2)
    mlist.pack(padx=padx, pady=pady, fill=BOTH, expand=YES)
    return mlist

def word_list(frame, height, select_proc, padx=0, pady=0):
    fr, list = scrolled_listbox(frame, height=height,
                                width=wordbox_width,
                                selectbackground=listbox_sel_bg)
    wrapped_bind(list, '<Button-1>', select_proc)     # proc already wrapped
    fr.pack(padx=padx, pady=pady, fill=BOTH, expand=YES)
    return list

# Adjust wordbox so index is near the center.  To avoid excessive
# bouncing around, don't move it if index is already viewable.
# When index is near the ends or completely out of view, then
# make an adjustment.

def center_word_view(wordbox, index, threshold=0.4):
    top, bottom = wordbox.yview()
    span = bottom - top
    midpt = (top + bottom) / 2
    csize  = wordbox.boxes[0].size()
    cindex = wordbox._concrete_index(index)
    frac = float(cindex) / max(csize, 1)
    if frac > midpt:
        # in bottom half: use lowest line of item
        cindex += wordbox.item_len[index] - 1
        frac = float(cindex) / max(csize, 1)
    if abs(frac - midpt) > threshold * span:
        wordbox.yview_moveto(frac - 0.5 * span)


# Wrap STRING over several lines (substrings) to fit in a CHAR_WIDTH
# space.  Try to pack extra words to take advantage of variable-width
# fonts.  Ensure that each substring is rendered within PIXEL_WIDTH
# using the given FONT.  Incrementally back off on initial scaling
# factors when a wrapped substring is found to be too long.
# Insert INDENT at front of subsequent substrings.
# Returns the list of substrings after the best fit is found.

def wrap_words(string, char_width, pixel_width, font, indent=''):
    initial = ''
    indent_len = len(indent)
    result = []
    while string:
        for d in range(5, -1, -1):     # do 1.5,1.4,...,1.0
            scaled_width = int((1.0 + d*0.1) * char_width)
            substrings = wrap(string, scaled_width,
                              initial_indent=initial,
                              subsequent_indent=indent)
            if font.measure(substrings[0]) <= pixel_width:
                break    # substring fits => keep it, else try narrower width
        result.append(substrings[0])
        string = ' '.join([ s[indent_len:] for s in substrings[1:] ])
        initial = indent
    return result


# Construct a top-level window to display text with scrollbars.  Accept
# a procedure for adding buttons (or other widgets) at the bottom.  The
# procedure is passed the parent frame.  The text widget object is returned
# for later use to insert text.  The toplevel frame is returned.

def scrolled_text_display(title='Text Display',
                          intro=None, aspect=2000, button_proc=null_proc,
                          horiz_scroll=0, barwidth=14,
                          width=70, height=24, geometry='-0+0',
                          tab_stops=(), enter_focus=1, **text_options):
    fr = Toplevel()
    fr.geometry(newGeometry=geometry)
    if intro:
        Frame(fr).pack(pady=2)
        Message(fr, aspect=aspect, text=intro).pack(padx=10, pady=5)
    button_proc(fr)    # assumes it will packed on bottom
    txt_fr = Frame(fr)
    widget_options = \
        merged_options(text_options, padx=10, pady=5,
                       wrap=WORD, state=NORMAL, font=text_font,
                       width=width, height=height, highlightthickness=0,
                       background=text_bg_color, tabs=tab_stops)
    txt = Text(txt_fr, **widget_options)
    scroll = FlatScrollbar(txt_fr, command=txt.yview, width=barwidth)
    txt.configure(yscrollcommand=scroll.set)
    txt.grid(row=0, column=0, sticky='news')
    if enter_focus and not on_win:
        wrapped_bind(fr, '<Enter>', lambda event: txt.focus_set())
    txt_fr.rowconfigure(0, weight=1, minsize=0)
    scroll.grid(row=0, column=1, sticky='ns')
    txt_fr.columnconfigure(0, weight=1, minsize=0)
    txt_fr.columnconfigure(1, weight=0, minsize=0)
    if horiz_scroll:
        hscroll = FlatScrollbar(txt_fr, command=txt.xview,
                                width=barwidth, orient=HORIZONTAL)
        txt.configure(xscrollcommand=hscroll.set)
        hscroll.grid(row=1, column=0, sticky='ew')
        txt_fr.rowconfigure(1, weight=0, minsize=0)
    txt_fr.pack(padx=5, pady=4, fill=BOTH, expand=YES)
#    button_proc(fr)
    fr.title(string=title)
    return fr, txt


# Construct a top-level window to display an arbitrary dialog.  A procedure
# is supplied to build the dialog widgets.  This procedure is passed the
# parent frame.  The dialog widget objects are returned for later use by
# the caller.  The toplevel frame is also returned.  Two additional procedures
# are supplied to validate the user's input on a normal close and to take
# final action when the dialog is closed.  Argument "results" is a list for
# passing back result values.  The first element is a boolean set to the
# OK/cancel selection.  The others are used/set by the widgets or callbacks.
# If geometry information is provided, it will be used for positioning;
# otherwise, the dialog will be centered relative to the main window.

def positioned_dialog(master, results=[0], geometry=None, use_grab=0,
                      close_text=close_button_text, top_pady=5,
                      use_cancel=0, cancel_default=0,
                      other_buttons=(), default_button=1,
                      title='Dialog Display', bind_return=1,
                      dialog_proc=null_proc,
                      validation_proc=lambda fr: True,
                      final_action=null_proc,
                      width=300, height=200, **other_options):
    fr = Toplevel()
    fr.title(string=title)
    if top_pady:
        Frame(fr).pack(pady=top_pady)

    def close_dialog(status, *args):
        results[0] = status
        if not status or validation_proc(fr):
            # assumes caller has access to data
            final_action(fr)       # called even in cancel case
            fr.destroy()
        # if input not valid, keep dialog alive
    normal_close = lambda *args: close_dialog(1)
    cancel_close = lambda *args: close_dialog(0)
    if cancel_default: default_close = cancel_close
    else:              default_close = normal_close
    if bind_return:
        wrapped_bind(fr, '<Return>', default_close)
    fr.protocol('WM_DELETE_WINDOW', default_close)

#    Frame(fr).pack(pady=2, side=BOTTOM)
    if use_cancel:
        cancel_button = (('Cancel', cancel_close),)
    else:
        cancel_button = ()
    buttons = ((close_text, normal_close),) + other_buttons + cancel_button
    but_fr, but_widgets = button_row(fr, buttons, use_default=default_button)
    but_fr.pack(fill=X, padx=20, pady=5, side=BOTTOM)

    fr.withdraw()
    widgets = dialog_proc(fr)   # optionally returns a sequence of widgets

    if geometry:
        fr.geometry(newGeometry=geometry)
    else:
        rx,ry = master.winfo_rootx(), master.winfo_rooty()
        if width == 0 or height == 0:   # 0 width means use actual width
            fr.update_idletasks()
            if fr.winfo_width() > 1:
                width  = fr.winfo_width()   
                height = fr.winfo_height()
            else:
                width  = fr.winfo_reqwidth()      # width not yet set
                height = fr.winfo_reqheight()
        if on_osx: y_offset = 20
        else:      y_offset = 30
        x = (master.winfo_width() - width) // 2
        # offset allows room for title bar
        y = (master.winfo_height() - height) // 2 - y_offset
        fr.geometry(newGeometry='+%d+%d'%(rx+max(0,x), ry+max(0,y)))

    if use_grab:
        fr.focus_set()
        fr.grab_set()
    fr.deiconify()
    return fr, widgets


# Add a row of buttons given a list of descriptor tuples
# (name, command [, disabled]).
# First button on list is default button.
# On Windows, buttons displayed in order given.
# On other platforms, they are reversed.
# Returns frame (unpacked), list of button widgets

def button_row(parent, butt_list, padx=5, size=2, use_default=1):
    button_fr = Frame(parent)
    widgets = []
    button_list = list(butt_list)
    default_index = 0
    if on_win:
        button_list.reverse()
        default_index = -1
    for button in button_list:
        command = EventHandler('Button: %s' % button[0], button[1])
        button_class = (ThinButton, MediumButton, FullButton)[size]
        w = button_class(button_fr, text=button[0], command=command,
                         default=NORMAL)
        if len(button) > 2 and button[2]:
            w['state'] = DISABLED
        w.pack(side=RIGHT, padx=padx)
        widgets.append(w)
    if use_default:
        widgets[default_index]['default'] = ACTIVE
    return button_fr, widgets


def set_scrollbars_top(widget):
    # following two motions needed to compensate for
    # balky scrollbar behavior on OS X Aqua
    widget.yview_moveto(1.0)
    widget.after(10, lambda : widget.yview_moveto(0.0))


# Display a list of messages in temporary window at bottom of main grid.

def show_temp_msg_panel(msgs, cancel_id, panel_set, padx=12, pady=6):
    panel, show_panel, hide_panel = panel_set
    panel.after_cancel(cancel_id)
    panel['padx'] = padx
    panel['pady'] = pady
    # derive aspect ratio needed for full list of messages
    wid = 80 - padx//6
    hts = reduce(add, map(lambda n: (n+wid)//wid, map(len, msgs)))
    # scaling factor is reduced from 100 to account for variable
    # character pixel width being smaller than height
    panel['aspect'] = (30 * wid) // (hts + len(msgs) - 1)
    panel['text'] = '\n\n'.join(msgs)
    show_panel()
    return panel.after(temp_warning_delay * len(msgs),
                       EventHandler('Hide msg panel', lambda : hide_panel()))


# Following is used to build dialogs having widgets that need
# to be disabled when controlling checkboxes are off.
# The dependency information is captured in var_dict.
# When a checkbox or other widget is set/reset, all of its
# dependent widgets are correspondingly enabled/disabled.
# var_dict is of the form:
#   {key -> (Tk var, var predicate, widget, [(key, widget),...])}
# The predicate should evaluate to true for enabling values of the
# Tk variable.

def update_dependents(w_name, var_dict):
    Tk_var, pred, widget, dep_list = var_dict[w_name]
    # need to use str() on the widget state because value is an
    # object rather than a string on the Windows platform
    if pred(Tk_var.get()) and str(widget['state']) != DISABLED:
        dep_state = NORMAL
    else:
        dep_state = DISABLED
    for dep_name, dep_widget in dep_list:
        dep_widget['state'] = dep_state
        if dep_name:
            update_dependents(dep_name, var_dict)    # cascade updates

# Update the state or other attributes of menubar items.  Tags are lists
# of indexes for traversing the cascading menus.

def update_menu_item(item_list, tag, **options):
    def update_entry(node, indexes):
        if len(indexes) == 1:
            node[0].entryconfigure(indexes[0], **options)
        else:
            update_entry(node[1+indexes[0]], indexes[1:])
    update_entry(item_list[1+tag[0]], tag[1:])

# Dynamically create a new submenu where only labels and commands are needed.

def update_submenu(tree, tag, item_list):
    def find_menu(tree, tag):
        if len(tag) == 1:
            return tree[1+tag[0]][0]
        else:
            return find_menu(tree[1+tag[0]], tag[1:])
    menu = find_menu(tree, tag)
    for entry, choice in enumerate(item_list):
        wrapped_cmd = EventHandler('Open Recent %s' % choice[0], choice[1])
        menu.entryconfigure(entry, label=choice[0], command=wrapped_cmd)


# ---------- Attribute-tagged Text widget insertion ---------- #

# The following features enable strings for insertion in Text widgets
# to be annotated with attribute tags.  The tags allow for substrings
# to be demarcated and associated with font and color attributes.  The
# tagged strings have the form <<label::string>>, where label names a
# predefined set of attributes.  Given a text widget and an annotated
# string, the insertion procedure will interpret the tagged portions
# and emit the Tkinter methods needed to insert each segment with the
# appropriate configuration settings.

_attrib_string_tag = re.compile('(?s)<<(\w+)::(.+?)>>')
                 
def insert_annotated_text(widget, atext):
    left = 0
    match = _attrib_string_tag.search(atext)
    while match:
        plain = atext[left:match.start()]
        if plain:
            widget.insert(END, plain)
        label, astring = match.groups()
        font, color = text_tag_attrib_defns.get(label, (text_font, 'black'))
        wtag = gensym()
        widget.insert(END, astring, (wtag,))
        widget.tag_configure(wtag, font=font, foreground=color)
        left = match.end()
        match = _attrib_string_tag.search(atext, left)
    if left < len(atext):
        widget.insert(END, atext[left:])


# ---------- Application menubar utilities ---------- #

# Menubar items are specified as a sequence of menus, each of which has
# the form [name, underline, choice1, ..., choiceN].  Each menu choice has
# the form (label, cmd, underline, optional ctrl char) or
# (label, list, underline) to indicate a cascading submenu.
# A choice of None indicates a separator.  A tag dictionary is created
# from the item names to save the list of indices needed to reach a
# menu item when changing its status or other configuration items.
# The underline value optionally can be (underline, postcommand).
# Ctrl char can be tuple (Key, Key-abbr) for cases such as (Escape, Esc).

def add_menubar(master, menubar, menus):   #
    tags = {}
    def make_menu(parent, indexes, name, under_post, *choices):
        if isinstance(under_post, int):
            menu = Menu(parent)
            underline = under_post
        else:
            menu = Menu(parent, postcommand=under_post[1])
            underline = under_post[0]
        parent.add_cascade(label=name, menu=menu, underline=underline)
        tags[name] = indexes
        tree = [menu]

        for entry, ch in enumerate(choices):
            if ch == None:
                menu.add_separator()
                tree.append(None)

            elif isinstance(ch[1], list):       # submenu
                tree.append(make_menu(menu, indexes + [entry],
                                      ch[0], ch[2], *ch[1]))

            else:   # ch = (label, cmd, underline, optional ctrl char)
                tags[ch[0]] = indexes + [entry]
                label = ch[0] + '    '
                wrapped_cmd = EventHandler('Menubar %s' % ch[0], ch[1])
                if len(ch) == 3:
                    menu.add_command(label=label, command=wrapped_cmd,
                                     underline=ch[2])
                elif isinstance(ch[3], tuple):
                    wrapped_bind(master, '<%s>' % ch[3][0],
                                 lambda event,cmd=wrapped_cmd: cmd(), 'Menu')
                    menu.add_command(label=label, command=wrapped_cmd,
                                     underline=ch[2], accelerator=ch[3][1])
                else:
                    wrapped_bind(master, '<Control-%s>' % ch[3],
                                 lambda event,cmd=wrapped_cmd: cmd(), 'Menu')
                    if on_osx:
                        wrapped_bind(master, '<Command-%s>' % ch[3],
                                     lambda event,cmd=wrapped_cmd: cmd(), 'Menu')
                        accel = 'Command-%s' % string.upper(ch[3])
                    else:
                        accel = 'Ctrl+%s' % string.upper(ch[3])
                    menu.add_command(label=label, command=wrapped_cmd,
                                     underline=ch[2], accelerator=accel)
                tree.append(None)
        return tree

# Collect menu object trees that emanate from top level menus.

    master.menubar_items = [None] + [ make_menu(menubar, [index], *items)
                                      for index, items in enumerate(menus) ]
    master.menu_tags = tags


# Create the top-level application menubar widgets.  Accommodate both
# OS X and Linux/Windows conventions.  Preferences and About items are
# handled separately.  Each argument is a tuple accepted by add_menubar:
# (menu item label, command proc, underline).
# Menus descriptor is a list with an entry for each app menu item.
# The value for each item is a list of tuples as accepted by add_menubar.

def make_app_menubar(master, menus, preferences, about, pref_sep=0, ab_sep=0):
    mbar = Menu(master, relief=FLAT)
    master.config(menu=mbar)
    if on_osx:
        # following option is to accommodate the OS X / Aqua menubar style
        mbar_id = master['menu']
        apple_id = mbar_id + '.apple'
        master.tk.call('menu', apple_id)
        master.tk.call(apple_id, 'add', 'command',
                       '-label', about[0],
                       '-command', master.register(about[1]))
        master.tk.call(apple_id, 'add', 'separator')

        pref_proc = master.register(preferences[1])
        if map(int, root.tk.eval('info patchlevel').split('.')) < [8,4,14]:
            master.tk.call(apple_id, 'add', 'command',
                           '-label', preferences[0],
                           '-accelerator', 'Command-,',
                           '-command', pref_proc)
            master.tk.call(apple_id, 'add', 'separator')
            wrapped_bind(master, '<Command-,>',
                         lambda ev, prefs=preferences[1] : prefs(), 'Prefs')
        else:
            # Since version 8.4.14, TkAqua hard codes the preference menu
            # item name.  Must insert Tcl code to call the Python function.
            master.tk.eval('proc ::tk::mac::ShowPreferences {} {%s}'
                           % pref_proc)
        master.tk.call(mbar_id, 'add', 'cascade', '-label', 'Apple',
                       '-menu', apple_id)
    else:
        for item in menus:
            if item[0] == 'Edit':
                if pref_sep: item.append(None)
                item.append(preferences)
            if item[0] == 'Help':
                if ab_sep: item.append(None)
                item.append(about)
    add_menubar(master, mbar, menus)
