#  Diagnil: Diagramless Crossword Assistant        Version 3.0
#      A utility for solving diagramless puzzles interactively
#
#  Copyright (c) 2003-2012, Ben Di Vito.  <bdivito@cox.net>
#
#  This is open source software, distributed under a BSD-style license.
#  See the accompanying file 'License' for details.
#

# ---------- Global definitions and startup actions ---------- #

from Tkinter import *

from tkFileDialog import askopenfilename, askopenfilenames, \
                         asksaveasfilename, askdirectory
from bisect import bisect_left  # , bisect_right
from operator import add
from StringIO import StringIO
from traceback import print_exc

import os, sys, pickle, copy, time, stat, string, re, glob

from diag_config    import *
from diag_messages  import *

class UserError(Exception):  pass
class FalseStart(Exception): pass
class OffNominal(Exception): pass
class NotACrossword(Exception): pass

# base_directory is the path to the application.  If run as a script,
# use the current working directory.

if sys.argv[0]:
    base_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    base_directory = os.getcwd()

on_win = sys.platform.startswith('win')   # Set options according to platform
on_osx = sys.platform      == 'darwin'
on_vista = on_win and sys.getwindowsversion()[0] >= 6  # includes Windows 7
on_linux = sys.platform.startswith('linux')

# user_directory is the (writeable) path to user-generated files.
# This works correctly for XP and other recent versions of Windows.
# For earlier ones such as Win98, it will use an approximation of
# the XP conventions, creating new directories as needed.  This is
# nonstandard but good enough for practical purposes.
# On Unix-based platforms, store files under ~/.diagnil.

if on_vista:
    home_directory = os.environ.get('USERPROFILE')
    if home_directory:
        user_directory = os.path.join(home_directory,
                                      'AppData', 'Roaming', 'Diagnil')
    else:
        home_directory = 'C:\\Users\\Public'
        user_directory = os.path.join(home_directory, 'Documents', 'Diagnil')
elif on_win:
    home_directory = os.environ.get('USERPROFILE',
                                    'C:\\Documents and Settings\\All Users')
    user_directory = os.path.join(home_directory, 'Application Data', 'Diagnil')
elif on_osx:
    home_directory = os.path.expanduser('~')
    user_directory = os.path.join(home_directory,
                                  'Library', 'Application Support', 'Diagnil')
else:
    # Linux and other Unix platforms
    home_directory = os.path.expanduser('~')
    user_directory = os.path.join(home_directory, '.diagnil')

def _copy_settings_file():
    import shutil
    if   on_win: settings_file = 'settings_win.py'
    elif on_osx: settings_file = 'settings_osx.py'
    else:        settings_file = 'settings_gen.py'
    shutil.copy(os.path.join(base_directory, settings_file),
                os.path.join(user_directory, 'settings.py'))

image_directory    = os.path.join(base_directory, 'images')
_sample_orig_dir   = os.path.join(base_directory, 'samples')
sample_puzzle_dir  = os.path.join(user_directory, 'samples')
default_puzzle_dir = os.path.join(user_directory, 'puzzles')

user_directory_error = 0
if not os.path.isdir(user_directory):
    # unless user directory exists, create it and then copy writeable
    # files and directories there
    import shutil
    try:
        os.makedirs(user_directory)
        _copy_settings_file()
        shutil.copytree(_sample_orig_dir, sample_puzzle_dir)
        os.mkdir(default_puzzle_dir)
        os.mkdir(os.path.join(user_directory, 'log'))
    except:
        user_directory_error = 1     # show error after startup
elif os.path.getmtime(_sample_orig_dir) > os.path.getmtime(sample_puzzle_dir):
    # sample directory was from previous version; refresh with new files
    import shutil
    _current = os.listdir(sample_puzzle_dir)
    for f in os.listdir(_sample_orig_dir):
        if f not in _current:
            shutil.copy2(os.path.join(_sample_orig_dir, f),
                         os.path.join(sample_puzzle_dir, f))
sys.path.insert(0, user_directory)

# On Macs, user can start the app from a disk image without installing.
# Note this fact so user can be asked on exit whether to delete files
# in user_directory.

user_trial_mode = on_osx and base_directory.startswith('/Volumes/Diagnil')

default_diag_ext  = '.dg0'
default_puz_ext   = ('.puz', '.pz0')
default_xpf_ext   = ('.xpf', '.xml')
default_ipuz_ext  = ('.ipuz',)
default_jpz_ext   = ('.jpz',)
default_puz_file_ext = default_puz_ext + default_xpf_ext + \
                       default_ipuz_ext + default_jpz_ext
puz_file_ext = ( '*' + default_diag_ext ,) + \
               tuple([ '*' + pe for
                       pe in default_puz_file_ext ])


# Application colors

master_bg       = '#e0e4e8'       # 
message_bg      = '#e2e9f0'       # AliceBlue @ 240
word_bg_color   = 'ghost white'   # same as text_bg
text_bg_color   = '#fbfbff'       # between white and ghost white (less bluish)
text_fg_color   = 'black'
outer_bg_color  = '#ffffdd'       # (pale yellow) for out-of-bounds region
temp_text_bg    = '#fffaf0'       # (pale yellow) for temp/preview bg
default_fg      = 'blue'
highlight_color = 'SteelBlue3'    # for entry widgets
block_color     = '#a6acb0'       # AliceBlue @ 176
                                  # less contrast/harshness than black
sym_block_color = '#d3dae0'       # AliceBlue @ 224
rule5_color     = 'SteelBlue3'    # lines  5, 15, ...
rule10_color    = 'SteelBlue4'    # lines 10, 20, ...
num_color       = 'RoyalBlue1'
placeholder_color = 'blue'        # placeholder chars on grids
custom_red      = '#be3232'       # alt: '#be3200'
cursor_color    = custom_red
clash_color     = custom_red      # for "clash dots"
error_color     = 'red'
msg_alert_color = 'red'           # for file name, date
msg_saved_color = 'DarkGreen'
marker_color    = highlight_color # to mark initial/final cells
region_color    = custom_red      # box for region movement
preview_color   = 'blue3'         # letters in preview (dragging) mode
block_pre_color = '#dcbebe'       # less saturated (35) than RosyBrown (62)
inferred_color  = custom_red      # when number inferable
num_exists_color = '#009933'      # when word number exists (greenish)
listbox_nogrid   = 'DarkRed'
listbox_minigrid = 'DarkBlue'
listbox_maingrid = 'DarkGreen'
listbox_sel_bg  = '#d0d6dc'       # default on XP is too dark
listbox_indicator = '#f8eae6'     # for highlighting listbox item
listbox_indic_key = '#d7f6ff'     # for highlighting key-cursor listbox item
key_cursor_color = '#7ddfff'      # for key-based navigation feature (cyan-ish)
dim_cursor_color = listbox_indic_key  # for inactive grid cursors


# ---------- Tk Initialization ---------- #

root = Tk()        # start Tk and save resulting object

root.option_add('*tearOff', FALSE)        # suppress tearoff menu feature

on_aqua = on_osx and root.tk.call('tk', 'windowingsystem') == 'aqua'

try:
    if on_aqua: root.tk.call('console', 'hide')
except:
    pass

# Derive application fonts relative to base family.

def font_var(delta, *options):
    return (font_fam, str(init_font_size+delta)) + options

# Font sizes in Windows appear around 4 pts larger than Linux:
import tkFont
if on_win:
    font_fam, init_font_size = 'Arial', 9  #'Verdana', 9
    num_font = ('Arial', '7')
    clash_font = ('Arial', '9', 'bold')
else:
    ref_font = tkFont.Font(root=root, font=('Helvetica',12,'bold'))
    M_I_width = ref_font.measure('M') + ref_font.measure('I')
    # scale target font size using empirically derived formula
    font_fam, init_font_size = 'Helvetica', int(round(180.0/M_I_width))
    num_font = font_var(-3)
    clash_font = font_var(-1)

if   on_win: grid_font = font_var(2, 'bold')
elif on_osx: grid_font = font_var(1)
else:        grid_font = font_var(0, 'bold')

menu_font, text_font = font_var(0), font_var(0)
bold_font  = font_var(0, 'bold')
small_text = font_var(-2)
small_bold = font_var(-2, 'bold')
italic_font = font_var(0, 'italic')

heading1_font,  heading2_font = font_var(1,'bold'), font_var(2, 'bold')

# Provide a function to estimate font-relative width of button text.

_button_ref_font = tkFont.Font(root=root, font=Button()['font'])
_button_ref_width = \
    (_button_ref_font.measure('M') + _button_ref_font.measure('i')) / 2.0

def button_width_estimate(text):
    return int(round(_button_ref_font.measure(text) / _button_ref_width))

# The following are used to tag and annotate Text widget strings.

text_tag_attrib_defns = {
    'blue'     : (text_font, 'dark blue'),
    'topic'    : (bold_font, 'dark blue'),
    'bold'     : (bold_font, 'black'),
    'italic'   : (italic_font, 'black'),
    'heading1' : (heading1_font, 'black'),
    'heading2' : (heading2_font, 'black'),
    }

# On Windows will be using either the new ttk package (Tk 8.5+) or
# the Tile package (Tk 8.4) for improved native look on XP and Vista.
# Also use ttk for Linux if available.  Defer use on OS X; there are
# still some problems.

using_ttk, using_tile = None, None

if on_win or on_linux:
    try:
        import ttk
#        from ttk import *  ### override all defaults with ttk widgets
        using_ttk = 1
    except:
        try:
            using_tile = root.tk.call('package', 'require', 'tile')
        except:
            pass

if on_win:
    # remove red Tk icon
    root.tk.call('wm', 'iconbitmap', root._w, '-default',
                 os.path.join(base_directory, 'diagnil.ico'))
elif using_ttk or using_tile:
    root.tk_setPalette('background', '#d9d9d9')
elif on_osx:
    root.tk_setPalette('background', master_bg)
else:
    root.tk_setPalette('background', master_bg)
    root.option_add('*font', text_font)

# If available, ttk or Tile versions of selected widgets
# will become the defaults.
theme_set = ''
if using_ttk:
    ttk_style = ttk.Style()
    if on_win:
        try:
            ttk_style.theme_use('xpnative')
            theme_set = 'xpnative'
        except:
            ttk_style.theme_use('winnative')
            theme_set = 'winnative'
    elif on_aqua:
        ttk_style.theme_use('aqua')
    else:
        ttk_style.theme_use('default')  ### or clam or alt

    # override selected widgets with ttk versions:
    from ttk import Button, Checkbutton, Entry, Radiobutton, Scrollbar
    from ttk import Menubutton


if using_tile:
    if on_win:
        try:
            root.tk.call('tile::setTheme', 'xpnative')
            theme_set = 'xpnative'
        except:
            root.tk.call('tile::setTheme', 'winnative')
            theme_set = 'winnative'
    elif on_aqua:
        root.tk.call('tile::setTheme', 'aqua')
    else:
        root.tk.call('tile::setTheme', 'alt')
    root.tk.call('namespace', 'import', '-force',
                 'ttk::button', 'ttk::checkbutton', 'ttk::dialog',
                 'ttk::entry', 'ttk::radiobutton', 'ttk::scrollbar')
#                'ttk::label', ttk::frame, 
#    root.tk.call('namespace', 'import', '-force', 'ttk::*')


#  User dialog procedures

if using_tile:
    # Tile-based dialogs are invoked with the help
    # of a few custom Tcl procedures.
    root.tk.call('source', os.path.join(base_directory, 'tile_dialogs.tcl'))
    
    # create analogs to procedures in library module tkMessageBox
    def showinfo(title='', message='', **options):
        return root.tk.call('tile_showinfo', title, message)
    def showwarning(title='', message='', **options):
        return root.tk.call('tile_showwarning', title, message)
    def showerror(title='', message='', **options):
        return root.tk.call('tile_showerror', title, message)
    def askokcancel(title='', message='', **options):
        return 'ok' == root.tk.call('tile_askokcancel', title, message)
else:
    from tkMessageBox import showinfo, showwarning, showerror, askokcancel


# ---------- User Preferences ---------- #

# Application window settings are loaded on startup and saved on exit.

try:
    preference_load_error = 0
    import settings
    app_settings = settings.app_settings
except:
    preference_load_error = 1     # problem with settings file, use defaults
    _copy_settings_file()
    import settings
    app_settings = settings.app_settings

app_geometry   = app_settings['geometry']
app_prefs_user = app_settings['preferences']     # settings seen by user
app_recent     = app_settings.get('recent', {})  # added in version 2.0
if not app_recent:
    app_settings['recent'] = app_recent

for pref, default in unadjusted_prefs:
    # preferences missing in settings files from older versions
    # will be set to default values:
    app_prefs_user[pref] = app_prefs_user.get(pref, default)

for setting, default in recent_settings:
    app_recent[setting] = app_recent.get(setting, default)

# Methods use a copy of the user preferences so they still see
# the current values even if the user edits the preferences.

app_prefs      = copy.deepcopy(app_prefs_user)

# Some preference values undergo adjustment before use to change units
# or perform other transformations.

def adjust_preferences():

    # convert delay from tenths to msec
    app_prefs['popup_delay']  = 100 * app_prefs_user['popup_delay']
    
    # puzzle directory can be relative or absolute
    direc = app_prefs_user['puzzle_folder']
    if os.path.isabs(direc):
        app_prefs['puzzle_folder'] = os.path.normpath(direc)
    else:
        app_prefs['puzzle_folder'] = os.path.join(user_directory, direc)

adjust_preferences()     # initial adjusted values    
    
root.geometry(app_geometry['main'])

# On application exit, regenerate the settings file to capture
# the user's preferred window settings.

def emit_new_settings():
    app_geometry['main'] = root.geometry()
    set_file = open(os.path.join(user_directory, 'settings.py'), 'w')
    print >> set_file, \
          '#\n# Do not edit!  File is regenerated dynamically.\n#'
    print >> set_file, 'app_settings = \\'
    print >> set_file, app_settings
    print >> set_file, ''
    set_file.close()


# When grid symmetry is enabled, cell row and column values are
# mapped by the following functions.
# Diagonal cases only work for square grids.

symmetry_mappings = {
    'rot'   : lambda r,c,nr,nc: (nr - r, nc - c) ,
    'horiz' : lambda r,c,nr,nc: (r, nc - c) ,
    'vert'  : lambda r,c,nr,nc: (nr - r, c) ,
    'ul-lr' : lambda r,c,nr,nc: (c, r) ,             # diagonal
    'ur-ll' : lambda r,c,nr,nc: (nc - c, nr - r) ,   # diagonal
}


# ---------- Global constants ---------- #

num_mini_grids = 4
num_grids      = 1 + num_mini_grids
main_grid_size = 30       # maximum grid extent
mini_grid_size = 20       
grid_size      = (main_grid_size,) + (mini_grid_size,) * num_mini_grids
grid_cursors   = ('sb_right_arrow', 'sb_down_arrow', 'tcross')

dir_text       = ('Across', 'Down')
placeholder    = '?'
no_num_symbol  = 'X'
null_word_symb = u'\N{white square}'
clue_separator = u'\N{black diamond}'
new_puz_file   = 'New puzzle'
num_recent     = 10     # max number of recent files to save

cell_size      = 26     # empirically determined
half_cell_size = cell_size // 2
cell_offset    = 15                  # for positioning single letter
clash_offsets  = (9, 20, 19, 11)     # for positioning clashing letter pair
wordbox_width  = 30     # adequate for most clues
wordbox_height =  5     # let height be stretched by grid companion
error_box_width = 2     # border thickness for erroneous word box

# Initial display size is 24 unless too big; adapt to actual screen size.

main_grid_show = \
    min(24, int((root.winfo_screenheight() - 150) / cell_size)) # 150 empirical

preview_delay   =  300   # msec before enabling dragging
visit_delay     =  500   # msec before action on mouse visiting a new cell
scroll_delay    = 1000   # msec before scrolling listbox and selecting word
key_scroll_delay = 500   # msec before scrolling listbox in key mode
msg_alert_delay = 5000   # msec to show msg highlighted
temp_word_delay = 5000   # msec to show temp inferred word
temp_warning_delay = 8000   # msec to show temporary warning message

num_adj_up_keysyms   = ('plus', 'KP_Add')
num_adj_down_keysyms = ('minus', 'KP_Subtract')
undisplayed_keysyms  = ('plus', 'minus', 'KP_Add', 'KP_Subtract')
undisplayed_keys     = ('+', '-')

null_cell       = [None, None, None]
null_proc       = lambda *args: None

modifier_keysym_pattern = re.compile('(.+)_')

canvas_tag_types  = (
    'letter', 'block', 'symm', 'aids', 'm_aids', 'preview', 'marker',
    'infer', 'infer2', 'visit', 'key_cursor', 'error', 'final')
num_prefix        = re.compile('\A\s*\d+')

if on_win or on_osx: close_button_text = 'OK'
else:                close_button_text = 'Close'

if on_osx:    # buttons 2 & 3 reversed on Mac
    right_button_down, right_button_up = '<Button-2>', '<ButtonRelease-2>'
else:
    right_button_down, right_button_up = '<Button-3>', '<ButtonRelease-3>'


# The following tables give estimates of word number growth as a function
# of grid row.  Roughly 4 word numbers per row are observed empirically.
# Growth is higher near the top of a grid, so a gentle curve is used to
# represent typical growth patterns.  A prefix of the curve is enumerated
# (first 21 rows) and a tail that asymptotes at 3 per row is assumed for
# the remaining rows.

word_nums_per_row = \
    (6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3)
word_nums_curve = \
    word_nums_per_row + (3,) * (main_grid_size - len(word_nums_per_row))
cum_word_nums_curve = [1]
for n in word_nums_curve:
    cum_word_nums_curve.append(cum_word_nums_curve[-1] + n)
cum_word_nums_curve = tuple(cum_word_nums_curve)


# ---------- Class definitions ---------- #

# EventHandler is a wrapper for procedures that are bound to Tkinter events.
# It provides for catching and logging of unhandled exceptions by writing a
# traceback to the debug log.  It optionally records execution times.

class EventHandler(object):
    def __init__(self, name, proc):
        self.name = name
        self.proc = proc

    def record_exception(self):
        debug_log("\n***** Handler '%s' raised an exception. *****\n"
                  % self.name)
        trace = StringIO()
        print_exc(100, trace)
        internal_error(trace.getvalue(), 'Event handlers')

    def tcl_error_handler(self):
        cross = sys.modules['__main__'].__dict__.get('cross')
        if cross and cross.sess.quitting: return
        self.record_exception()

    if collect_time_data:
        def __call__(self, *args):
            result = None
            start = time.time()
            try:
                result = self.proc(*args)
            except FalseStart:       # these are safely rejected user actions
                pass
            except TclError:
                self.tcl_error_handler()
            except:                  # unhandled exceptions land here
                self.record_exception()
            if self.proc.__name__ in exclude_time_data: return 
            emit_log_entry(start, time.time(), "handler '%s'" % self.name)
            return result
    else:
        def __call__(self, *args):
            result = None
            try:
                result = self.proc(*args)
            except FalseStart:       # these are safely rejected user actions
                pass
            except TclError:
                self.tcl_error_handler()
            except:                  # unhandled exceptions land here
                self.record_exception()
            return result

def wrapped_bind(widget, event, proc, name=''):
    if name:
        widget.bind(event, EventHandler(name, proc))
    elif isinstance(proc, EventHandler):
        widget.bind(event, proc)   # assumed to be already wrapped
    else:
        widget.bind(event, EventHandler('unnamed', proc))


# ---------- Utility procedures ---------- #

def file_time_display(secs):
    return time.strftime('Saved %H:%M %b %d', time.localtime(secs))

def update_msg_widget(widget, text, after_id, fg_color=msg_alert_color):
    ### foreground working for Labels under ttk?
    widget.after_cancel(after_id)
    widget.configure(text=text, foreground=fg_color)
    def restore_text_color():
        widget.configure(foreground=text_fg_color)
    return widget.after(msg_alert_delay,
                        EventHandler('Update message follow-up',
                                     restore_text_color))

# Merge a procedure's called option arguments with default options,
# overriding defaults having same keys.

def merged_options(options, **defaults):
    result = defaults.copy()
    result.update(options)
    return result


# Following variable is assigned a non-null cleanup procedure after
# the application classes are created.  OS X restores the arrow cursor
# after a user dialog.  Grid cursors need to be reset after a dialog.

user_dialog_cleanup = null_proc
def set_user_dialog_cleanup(proc):
    global user_dialog_cleanup
    user_dialog_cleanup = proc

user_message_log = []
def reset_user_message_log():
    del user_message_log[:]

_old_msg_threshold = 100
_total_msg_deleted = 0

def log_user_message(title, message):
    global _total_msg_deleted
    user_message_log.append(
        '%s  [ %s ]\n%s\n\n' %
        (time.strftime('%H:%M  %d %b %Y'), title, message))
    if len(user_message_log) > _old_msg_threshold:
        cutoff = _old_msg_threshold // 2
        _total_msg_deleted += cutoff
        user_message_log[cutoff] = \
            '****  %s old messages deleted  ****\n\n' % _total_msg_deleted
        del user_message_log[:cutoff]

if collect_time_data:
    def user_dialog(dialog_proc, title, message, *args, **nargs):
        if on_osx: root.update_idletasks()   # ensure widgets are displayed
        start = time.time()
        try:
            result = dialog_proc(title, message, *args, **nargs)
        except TclError:
            return None         # TclError can happen when app closes
        emit_log_entry(start, time.time(),
                       'User dialog: %s' % dialog_proc.__name__)
        log_user_message(title, message)
        user_dialog_cleanup()
        return result
else:
    def user_dialog(dialog_proc, title, message, *args, **nargs):
        if on_osx: root.update_idletasks()   # ensure widgets are displayed
        try:
            result = dialog_proc(title, message, *args, **nargs)
        except TclError:
            return None         # TclError can happen when app closes
        log_user_message(title, message)
        user_dialog_cleanup()
        return result

# Construct a top-level window to display text with scrollbars.  Accept
# a procedure for adding buttons (or other widgets) at the bottom.  The
# procedure is passed the parent frame.  The text widget object is returned
# for later use to insert text.  The toplevel frame is optionally returned.

def _scrolled_text_display(title='Diagnil Text Display',
                           intro=None, button_proc=null_proc,
                           tab_stops=(), return_frame=0):
    fr = Toplevel()
    fr.geometry(newGeometry='-0+50')
    if intro: Label(fr, text=intro).pack(padx=10, pady=10)
    txt_fr = Frame(fr)
    if on_win:
        txt = Text(txt_fr, width=70, padx=10, pady=5, wrap=WORD,
                   tabs=tab_stops)
    else:
        txt = Text(txt_fr, width=70, padx=10, pady=5, wrap=WORD,
                   background=text_bg_color, tabs=tab_stops)
    scroll = Scrollbar(txt_fr, command=txt.yview)
    txt.configure(yscrollcommand=scroll.set)
    wrapped_bind(fr, '<Key-Prior>', lambda event: txt.yview_scroll(-1, PAGES))
    wrapped_bind(fr, '<Key-Next>',  lambda event: txt.yview_scroll(1, PAGES))
    wrapped_bind(fr, '<Enter>', lambda event: fr.focus_set())
    txt.pack(side=LEFT, fill=BOTH, expand=YES)
    scroll.pack(side=LEFT, fill=Y)
    txt_fr.pack(padx=5, pady=5, fill=BOTH, expand=YES)
    button_proc(fr)
    fr.title(string=title)
    if return_frame: return fr, txt
    else:            return txt


# ------------ Error handling ------------ #

def eval_assertion(assertion, label):
    if check_assertions:
        start = time.time()
        result = assertion()
        if result:
            stop = time.time()
            emit_log_entry(start, stop,
                           "checking assertion '%s'\n%s" % (label, result))
            assert False, label

def emit_log_entry(start, stop, entry_text):
    duration = stop - start
    if duration >= 1.0:
       num_text = '-- %6.1f  sec --' % duration
    else:
       num_text = '-- %6d usec --' % int(duration * 1000000)
    debug_log(time.strftime('%H:%M:%S', time.localtime(start)),
              num_text, entry_text)

_debug_values = []

def _preprocess_value(val):    # make tuples safe for %-operator
    if isinstance(val, tuple): return repr(val)
    else: return val
           
def debug_log(*values):
    _debug_values.append(
        reduce(add, map(lambda v: ' %s' % v,
                        map(_preprocess_value, values))) + '\n')

_internal_error_count = 0
_error_file_name = ''

def internal_error_proc(log_string, title, show=1):
    global _internal_error_count, _error_file_name
    _internal_error_count += 1
    if _internal_error_count > 5: return     ### stop runaway errors
    # unhandled exceptions in lines below may invoke this function recursively
    debug_log('\n-------------------------------\n')
    debug_log(log_string)
    debug_log('-------------------------------\n')
    _error_file_name = time.strftime('err-%H%M-%d%b%y.txt', time.localtime())
    try:
        debug_file = \
            open(os.path.join(user_directory,'log',_error_file_name), 'w')
        debug_file.write(
            time.strftime('Log file created at %H:%M on %d %b %Y\n\n',
                          time.localtime()))
        debug_file.write('Diagnil version: %s\n\n' % version)
        for item in _debug_values:
            debug_file.write(item)
        cross = sys.modules['__main__'].__dict__.get('cross')
        if cross:
            invariant_details = cross.state_invariant_details()
            if invariant_details == 0:
                invariant_details = 'Invariant has been maintained.\n\n'
            debug_file.write('\n\nState invariant check:\n\n')
            debug_file.write(invariant_details)
            debug_file.write('\n\n-------- Dump of perm object --------\n')
            debug_file.write('%s\n' % version)
            pickle.dump(cross.perm, debug_file)
            debug_file.write('\n-------- End of perm object --------\n')
        
            if cross.temp.recovery_state:        # action was partial
                cross.install_perm(cross.temp.recovery_state, 0)
                cross.temp.recovery_state = None
        debug_file.close()
    except:
        pass   # if logging fails, we're too far gone to recover
    if show:
        err_msg = user_dialog(showerror, title,
                              display_messages['internal_error'])
    _internal_error_count -= 1

def internal_error(log_string, title, show=1):
    try:
        internal_error_proc(log_string, title, show)
    except TclError:
        pass         # can happen when app closes

def display_reporting_procedure(*args):
    no_log_file = not _error_file_name
    path_name = os.path.join(user_directory, 'log', _error_file_name)
    size=500
    fr = Toplevel(height=size, width=size)
    fr.title(string='Diagnil Problem Reporting Procedure')
    Message(fr, aspect=300,
            text=display_messages['reporting_procedure']
            ).pack(padx=10, pady=10)

    def copy_entry_clipboard(ent):
        ent.selection_range(0, END)        # for Unix/Linux
        ent.clipboard_clear()
        ent.clipboard_append(ent.get())    # needed for Windows
    if using_ttk or using_tile:
        addr_ent = Entry(fr, background=text_bg_color, width=60)
    else:
        addr_ent = Entry(fr, background=text_bg_color, width=60, relief=SUNKEN)
    addr_ent.insert(END, email_addr)
    addr_ent.pack(padx=20, pady=5)
    fr_email = Frame(fr)
    Button(fr_email, text='Copy',
           command=EventHandler('Reporting proc',
                                lambda : copy_entry_clipboard(addr_ent))
           ).pack(side=LEFT, padx=5)
    Label(fr_email, text='E-mail Address to Clipboard').pack(side=LEFT, padx=5)
    fr_email.pack(pady=5)
    Frame(fr).pack(pady=5)
    
    if using_ttk or using_tile:
        file_ent = Entry(fr, background=text_bg_color, width=60)
    else:
        file_ent = Entry(fr, background=text_bg_color, width=60, relief=SUNKEN)
    file_ent.insert(END, path_name)
    file_ent.pack(padx=20, pady=5)
    fr_file = Frame(fr)
    copy_file_button = \
        Button(fr_file, text='Copy',
               command=EventHandler('Reporting proc',
                                    lambda : copy_entry_clipboard(file_ent)))
    copy_file_button.pack(side=LEFT, padx=5)
    Label(fr_file, text='File name to Clipboard').pack(side=LEFT, padx=5)
    fr_file.pack(pady=5)
    if no_log_file:
        file_ent['state'] = DISABLED
        copy_file_button['state'] = DISABLED
    Frame(fr).pack(pady=5)
    
    Message(fr, aspect=800,
            text=display_messages['privacy_notice']).pack(padx=10, pady=5)
    if using_ttk or using_tile:
        close_button = Button(fr, text=close_button_text, default=ACTIVE,
                              command=EventHandler('Reporting proc',
                                                   lambda : fr.destroy()))
    else:
        close_button = Button(fr, text=close_button_text, default=ACTIVE,
                              width=6,
                              command=EventHandler('Reporting proc',
                                                   lambda : fr.destroy()))
    close_button.pack(side=RIGHT, padx=30, pady=10)
    wrapped_bind(fr, '<Return>', lambda *ev: fr.destroy())
    rx,ry = root.winfo_rootx(), root.winfo_rooty()
    x = (root.winfo_width() - size) // 2
    y = (root.winfo_height() - size) // 2
    fr.geometry(newGeometry='+%d+%d'%(rx+x, ry+y))


# -------------- Development only --------------- #

_debug_disclaimer = \
    'For development use only; you may safely ignore or delete this window.'

def _display_debug_list(*args):
    def add_buttons(fr):
        but_fr = Frame(fr)
        Button(but_fr, text='Clear List', command=lambda : clear_all()) \
            .pack(side=LEFT, padx=5, pady=2)
        Button(but_fr, text='Refresh', command=lambda : show_all()) \
            .pack(side=LEFT, padx=5, pady=2)
        but_fr.pack()
    txt = _scrolled_text_display(title='Debug Log for Diagnil',
                                 intro=_debug_disclaimer,
                                 button_proc=add_buttons)
    def clear_all():
        global _debug_values
        _debug_values = []
        txt.delete(1.0, END)
    def show_all():
        txt.delete(1.0, END)
        for v in _debug_values: txt.insert(END, v)
        txt.insert(END, '\nTotal of %d entries\n' % len(_debug_values))
        txt.yview_moveto(1.0)
    show_all()

 # Bindings for debug features aren't wrapped.

def _display_debug_eval(*args):
    expr_above, expr_below = [], []
    ent = [None]
    def add_buttons(fr):
        but_fr = Frame(fr)
        if using_ttk or using_tile:
            ent[0] = Entry(but_fr, width=80)
        else:
            ent[0] = Entry(but_fr, width=80, highlightthickness=3,
                           background=word_bg_color,
                           highlightcolor=highlight_color)
        ent[0].pack(padx=5, pady=2)
        Button(but_fr, text='Clear Display', command=lambda : clear_all()) \
            .pack(pady=2)
        but_fr.pack()
    fr, txt = _scrolled_text_display(title='Debug Evaluator for Diagnil',
                                     intro=_debug_disclaimer,
                                     button_proc=add_buttons, return_frame=1)
    def clear_all():
        txt.delete(1.0, END)
    def eval_expr(dummy):
        expr = ent[0].get()
        ent[0].delete(0, END)
        expr_above.extend(expr_below)
        expr_above.append(expr)
        del expr_below[:]
        trace = StringIO()
        try:
            value = eval(expr)
            txt.insert(END, '------------------\n%s =\n' % expr + \
                       '%s\n' % repr(value))
        except:
            print_exc(1, trace)
            txt.insert(END, '------------------\n%s =\n' % expr)
            txt.insert(END, trace.getvalue()) 
        txt.yview_moveto(1.0)
    def prev_expr():
        ent[0].delete(0, END)
        if expr_above:
            prev = expr_above[-1]
            del expr_above[-1]
            expr_below.insert(0, prev)
            ent[0].insert(0, prev)
    def next_expr():
        ent[0].delete(0, END)
        if expr_below:
            next = expr_below[0]
            del expr_below[0]
            expr_above.append(next)
            ent[0].insert(0, next)
    def key_press(event):
        if event.keysym in ('Up','KP_Up'):
            prev_expr()
        elif event.keysym in ('Down','KP_Down'):
            next_expr()
    ent[0].bind('<Key>',    lambda event: key_press(event))
    ent[0].bind('<Return>', lambda event: eval_expr(event))
    ent[0].bind('<Control-u>', lambda event: ent[0].delete(0, END))
    fr.bind('<Enter>', lambda event: ent[0].focus_set())

def _generate_test_error(*args):
    try:
        1 / 0
    except:
        trace = StringIO()
        print_exc(100, trace)
        internal_error(trace.getvalue(), 'Test error', 0)

root.bind('<Shift-F2>', _display_debug_list)   # Shift-F2 fails on Linux
root.bind('<Shift-F3>', _display_debug_eval)
root.bind('<Shift-F4>', lambda *args: cross.export_to_json())
root.bind('<Control-F2>', _display_debug_list)
root.bind('<Control-F3>', _display_debug_eval)
root.bind('<Control-F4>', lambda *args: cross.export_to_json())
root.bind('<Control-F9>', _generate_test_error)

def exec_string(string, module='__main__'):
    exec string in sys.modules[module].__dict__

def delete_old_log_files():
    log_dir = os.path.join(user_directory, 'log')
    log_files = os.listdir(log_dir)
    old_files = []
    cutoff_time = time.time() - 30*24*3600     # 30 days ago
    for file in log_files:
        path = os.path.join(log_dir, file)
        if os.path.getmtime(path) < cutoff_time:
            try:
                os.remove(path)
                old_files.append(file)
            except IOError:
                pass    #### log failure?
    entry = 'Deleting old log files:\n' + '\n'.join(old_files)
    debug_log(time.strftime('%H:%M:%S', time.localtime()), entry)

def emit_log_file():
    if not (check_assertions or collect_time_data): return
    file_name = time.strftime('%H.%M_%d-%b-%Y', time.localtime())
    log_file = open(os.path.join(user_directory, 'log', file_name), 'w')
    log_file.write('Automatic log of Diagnil development version %s.\n' \
                   % version)
    log_file.write(time.strftime('Log file created at %H:%M on %d %b %Y\n\n',
                                 time.localtime()))
    log_file.write('All measured durations are elapsed times in '
                   'seconds or microseconds.\n\n')
    for item in _debug_values: log_file.write(item)
    log_file.close()

# Following are for test only.

def _test_run_time(n, proc=null_proc):
    # elapsed time in usec to run proc n times
    i = 0
    start = time.time()
    while i < n:
        proc(i)
        i += 1
    stop = time.time()
    debug_log(time.strftime('%H:%M:%S', time.localtime(start)),
              '  Elapsed time = %6d usec' % int((stop - start) * 1000000),
              ' test run time')

def _paint_dot(canv, i, j, color):
    x,y = (j+1)*cell_size - 4, (i+1)*cell_size - 4
    canv.create_oval(x-2, y-2, x+2, y+2, tags=('test',),
                     outline=color, fill=color)

def _scale_color(color, factor):
    rgb = root.winfo_rgb(color)
    return '#%02x%02x%02x' % \
              tuple(map(lambda c: min(int(round((c%256)*factor)), 255), rgb))

_attr_cache = {}

def getfn(name):
    if name in _attr_cache:
        return _attr_cache[name]
    for m in sys.modules.values():
        try:
            attr = getattr(m, name)
        except AttributeError:
            continue
        _attr_cache[name] = attr
        return attr
    raise AttributeError

dir_fn = dir
