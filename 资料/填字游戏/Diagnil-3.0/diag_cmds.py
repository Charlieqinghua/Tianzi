#  Diagnil: Diagramless Crossword Assistant        Version 3.0
#      A utility for solving diagramless puzzles interactively
#
#  Copyright (c) 2003-2012, Ben Di Vito.  <bdivito@cox.net>
#
#  This is open source software, distributed under a BSD-style license.
#  See the accompanying file 'License' for details.
#

#
# ----------  Main command handlers ---------- #
#

from diag_globals   import *
from diag_util      import *
from diag_classes   import *
from diag_readpuz   import PuzzleDefn
if on_osx: from Carbon import AE


helpDict = None     # help topics not loaded until needed

_about_text_1 = 'Version %s\n%s' % (version, release_date)

_about_text_2 = u'''Diagramless Crossword Assistant

Copyright \N{Copyright Sign} %s, Ben Di Vito.
''' % copyright_dates


app_app = None

# ---------- Class definitions ---------- #

class DiagCommands(object):
    def __init__(self, master):
        if on_aqua:
            # Replace Tcl's exit command with an exit procedure
            # that calls the exit method in this module.
            # Following saves Tcl commands to file, then sources them.
            # Awkward, but using tk.call doesn't work.
            tcl_exit = self.master.register(lambda : self.exit())
            aqua_quit = os.path.join(user_directory, 'aqua_quit.tcl')
            quit_file = open(aqua_quit, 'w')
            quit_cmds = ('rename exit exit.orig',
                         'proc exit {} {%s}' % tcl_exit)
            for q_cmd in quit_cmds:
                print >> quit_file, q_cmd
            quit_file.close()
            master.tk.call('source', aqua_quit)


# ---------- File/puzzle maintenance commands ---------- #

    def need_to_save(self):
        if self.temp.needs_saving: return 1
        saved = self.temp.last_saved
        # don't use !=  in following comparison:
        return (not self.perm == saved) and \
               (self.perm.has_content() or 
                isinstance(saved, PermState) and saved.has_content())

    def ok_to_overwrite(self, check_need=1):
        return check_need and not self.need_to_save() or \
               user_dialog(askokcancel, *dialog_messages['confirm_close'])

    def clear(self, check=1, clear_entries=1):
        # Erase all grids and initialize puzzle state
        if check and not self.ok_to_overwrite(): return 0
        for i in range(num_grids):
            for item_type in canvas_tag_types:
                self.gui.grids[i].delete(item_type)
        if clear_entries:
            for dir in (0,1):
                self.sess.word_entry_text[dir] = ''
                self.temp.sel_num_word[dir] = None
                self.gui.word_ent[dir].delete(0, END)
                self.gui.pattern_ent[dir].delete(0, END)
        for dir in (0,1):
            self.gui.wordbox[dir].delete(0, END)
            self.gui.searchbox[dir].delete(0, END)
        self.perm = PermState()
        self.aux  = AuxState()
        if self.sess.key_navigation:         # display initial key cursors
            for canv in self.gui.grids:
                paint_key_cursor(canv, 2, 0, 0, 'letter')
        return 1   # indicate success

    def new_clueless(self, check=1, clear=1, initialized=1):
        if self.clear(check, clear):
            self.temp = TempState()
            self.gui.configure_title_line('')
            self.new_puzzle_file()
            self.update_word_counts()
            # use sess attribs, set temp.size_symm:
            self.set_puzzle_size(use_session=2)

            self.temp.last_saved = copy.deepcopy(self.perm)
            self.set_menu_item_state(DISABLED, *self.dynamic_menu_items)
            self.show_main_grid()
            if initialized:
                if self.sess.focus_region == 1:
                    self.sess.next_focus = 1    # in Down panel
                else:
                    self.sess.next_focus = 0
                self.toggle_entry_focus()
            self.start_timer()

    def open_puz(self, puz_file=None, puz_content='',
                 alt_dir='', file_types=None):
#        if puz_content:
#            pass                 # downloaded file contents
        if not self.ok_to_overwrite():
            return
        if alt_dir and not os.path.isabs(alt_dir):
            alt_dir = app_recent[alt_dir]    # retrieve directory from settings
        if puz_file == None:
            initial_dir = alt_dir or self.sess.puzzle_dir
            if not file_types:
                file_types = [("Diagramless Puzzle Files", puz_file_ext),
                              ("All Files", "*")]
            puz_file = askopenfilename(filetypes=file_types,
                                       title='Open puzzle file',
                                       initialdir=initial_dir)
        elif os.path.isabs(puz_file):
            pass
        elif puz_file == '':
            return    # null case for empty recent file list
        else:
            for direc in (self.sess.latest_puz_dir, self.sess.puzzle_dir,
                          default_puzzle_dir):
                path = os.path.join(direc, puz_file)
                if os.path.exists(path):
                    puz_file = path
                    break
        if not puz_file and not puz_content: return

        # reset menu items first in case load fails
        self.set_menu_item_state(DISABLED, *self.dynamic_menu_items)
        file_ext = os.path.splitext(puz_file)[1].lower()

        try:
            if file_ext in default_puz_file_ext or puz_content:
                self.new_clueful(puz_file, puz_content)
            elif file_ext == default_diag_ext:
                self.open_diag_puz(puz_file)
            else:
                self.open_diag_puz(puz_file)
        except FalseStart:
            self.gui.configure_title_line('')
            return           # error message already emitted

        self.show_main_grid()
        if self.sess.focus_region == 1:
            self.sess.next_focus = 1    # in Down panel
        else:
            self.sess.next_focus = 0
        self.toggle_entry_focus()
        self.temp.puz_file = puz_file
        self.temp.last_saved = copy.deepcopy(self.perm)
        self.update_window_title()
        self.gui.solving_time['text'] = timer_display(self.temp.solv_time)
        if self.temp.puz_defn:
            soln_words = self.temp.puz_defn.soln_words
            if soln_words:
                self.temp.soln_letter_count = \
                    max(sum([ len(w) for w in soln_words[0].values() ]),
                        sum([ len(w) for w in soln_words[1].values() ]))
            else:
                # scanned-clue puzzle has no solution words
                self.temp.soln_letter_count = 100000

        nwords = [ str(len(self.perm.posns[i][0]) + len(self.perm.posns[i][1]))
                   for i in range(num_grids) ]
        self.gui.status_line['text'] = \
            'Number of words on grids:  %s' % ', '.join(nwords)
        if puz_content:
            self.eph.save_time_id = update_msg_widget(self.gui.save_time_msg,
                                                      'Not yet saved',
                                                      self.eph.save_time_id)
        else:
            time_text = file_time_display(os.stat(puz_file)[stat.ST_MTIME])
            self.eph.save_time_id = \
                update_msg_widget(self.gui.save_time_msg, time_text,
                                  self.eph.save_time_id,
                                  fg_color=msg_saved_color)
            if alt_dir != sample_puzzle_dir:
                # following performed only when file is not a sample puzzle
                self.update_recent_list(puz_file)
                new_latest_dir = os.path.dirname(puz_file)
                if new_latest_dir != self.sess.puzzle_dir:
                    app_recent['latest_puzzle_dir'] = new_latest_dir

        self.emit_warnings()
        self.eph.warnings = {}
        if not self.perm.final:
            self.start_timer()


    def open_diag_puz(self, puz_file):
        reraise = 0
        try:
            ifile = open(puz_file, 'rb')  # binary mode needed for pickle
        except EnvironmentError:
            user_dialog(showerror, *error_msg_sub('invalid_open', puz_file))
            raise FalseStart
        try:
            # retrieve stored version number from first line
            ifile_version = ifile.readline().strip()
            if ifile_version.startswith('%Diagnil-'):
                # added identifying prefix in version 3.0
                ifile_version = ifile_version[9:]
            ifile_version_list = map(int, ifile_version.split('.'))
            if ifile_version_list < last_file_version_change:
                # file version obsolete -- can't open
                user_dialog(showerror, *error_msg_sub('old_file_version',
                                                      ifile_version))
                reraise = 1
            else:
                perm = pickle.load(ifile)
                self.temp = TempState()
                self.install_saved_perm(perm)

        except:   ## Various exceptions possible when unpickling
            trace = StringIO()
            print_exc(100, trace)
            debug_log("\n*** Unpickling '%s' raised an exception. ***\n%s"
                      % (puz_file, trace.getvalue()))

            user_dialog(showerror, *error_msg_sub('corrupted_open',
                                                  os.path.basename(puz_file)))
            ifile.close()
            self.clear(0)        # remove state from partial load
            raise FalseStart
        ifile.close()
        if reraise:
            raise FalseStart

    def new_clueful(self, puz_file, puz_content):
        def show_open_error(msg_name):
            user_dialog(showerror,
                        *error_msg_sub(msg_name, os.path.basename(puz_file)))

        base, ext = os.path.splitext(puz_file)
        ext = ext.lower()
        try:
            puz_defn = PuzzleDefn(puz_file, self.eph.warnings,
                                  puz_content, file_ext=ext)
        except IOError:
            show_open_error('corrupted_open')
            raise FalseStart
        except ValueError:
            msg = 'jpz_file_not_diagramless' if ext == '.jpz' \
                  else 'puz_file_not_diagramless'
            use_anyway = user_dialog(askokcancel, *dialog_messages[msg])
            if use_anyway:
                puz_defn = PuzzleDefn(puz_file, self.eph.warnings,
                                      puz_content, file_ext=ext, use_anyway=1)
            else:
                raise FalseStart
        except OffNominal:
            show_open_error('unsupported_open')
            raise FalseStart
        except NotACrossword:
            show_open_error('not_a_crossword')
            raise FalseStart
        except:       # most likely an ill-formed puzzle file
            show_open_error('open_unknown_variant')
            raise FalseStart

        if not self.clear(0): return

        self.temp = TempState()
        self.temp.last_saved = self.perm     # until copy is made
        self.temp.puz_defn = puz_defn
        self.install_clues(puz_defn)
#        self.temp.needs_saving = 1
        self.update_word_counts()
        self.set_puzzle_size(use_session=0)

        self.gui.puzzle_size['text'] = self.current_puzzle_size()
        eval_assertion(self.state_invariant, 'Post-installation check')

    def install_clues(self, puz_defn, insert_clues=1):
        if insert_clues:
            self.enter_clues(puz_defn)
        if not self.temp.size_symm:
            self.temp.size_symm = (self.sess.show_boundary,
                                   self.sess.apply_symmetry,
                                   puz_defn.symmetry_type,
                                   puz_defn.width,
                                   puz_defn.height)

        if puz_defn.soln_words:      # fully clueful
            self.set_menu_item_state(NORMAL, *self.clueful_menu_items)
            if puz_defn.soln_flags:
                self.set_menu_item_state(NORMAL, 'Unlock Solution...')
            else:
                self.set_menu_item_state(NORMAL, *self.solution_menu_items)
        elif puz_defn.soln_posns:    # ipuz without solution
            self.set_menu_item_state(NORMAL, *self.clueful_menu_items)
        else:                        # semi-clueful mode (scanned)
            self.set_menu_item_state(NORMAL, *self.semi_clueful_menu_items)
        if puz_defn.copyright.startswith(u'\N{Copyright Sign}'):
            copyright_string = puz_defn.copyright
        else:
            copyright_string = u'\N{Copyright Sign} %s' % puz_defn.copyright
        self.gui.configure_title_line(puz_defn.title, puz_defn.author,
                                      copyright_string)

    def install_saved_perm(self, perm):
        if getattr(perm, 'final', None) == None:
            perm.final = ()                # upgrade older file formats

        if getattr(perm, 'size_symm', None) in (None, ()):
            # for older file formats, which lack this attribute
            perm.size_symm = (0, 0, 'rot', 0, 0)

        if not getattr(perm, 'puz_defn', None):
            perm.puz_defn = None           # upgrade older file formats
            self.gui.configure_title_line('')

        if not getattr(perm, 'alt_words', None):
            perm.alt_words = [{},{}]       # upgrade older file formats

        if not getattr(perm, 'solv_time', None):
            perm.solv_time = 0             # upgrade older file formats

        perm_to_temp(perm, self.temp)
        puz_defn = self.temp.puz_defn
        if puz_defn:
            format_type = getattr(puz_defn, 'format_type', None)
            if not format_type:
                # format_type not added until version 2.4
                puz_defn.format_type = determine_format_type(puz_defn)
            self.install_clues(puz_defn, insert_clues=0)
        self.install_perm(perm, clear_entries=1)

    def install_perm(self, perm, clear_entries=1, redo=0):
        if not isinstance(perm, PermState):
            # this case shouldn't happen; possibly perm was None;
            # try to recover silently but things will break elsewhere
            trace = StringIO()
            print_exc(100, trace)
            debug_log("\n***** Invalid Perm object: *****\n\n%s\n\n%s\n"
                      % (perm, trace.getvalue()))
            perm = PermState()

        # Install puzzle from saved state by rebuilding it
        self.clear(0, clear_entries)
        self.perm.posns = perm.posns
        self.perm.grid_id = perm.grid_id
        self.perm.alt_words = perm.alt_words

        if app_prefs['upper_case']: trans = lambda s: s.upper()
        else:                       trans = lambda s: s.lower()
        for dir in 0,1:
            words = perm.words[dir]
            for n, w in perm.words[dir].items():
                target = trans(w)
                if w != target: words[n] = target
        if self.temp.puz_defn:
            self.enter_words_clues(perm)
        else:
            self.enter_words(perm)
        self.place_blocks(perm)
        self.perform_followup_actions()
        self.update_word_counts()

        if perm.final:
            if type(perm.final) == tuple:
                self.perm.blocks[0] = perm.final[2]
                self.place_blocks(self.perm)
            else:
                perm.final = (0, 0, {})
            self.finalize_puzzle(perm.final, 0)

        if not redo:
            self.set_puzzle_size(use_session=0)
        if self.temp.size_symm[1]:              # apply_symmetry flag
            self.add_symmetric_blocks()

        self.gui.puzzle_size['text'] = self.current_puzzle_size()
        eval_assertion(self.state_invariant, 'Post-installation check')

    def save_as(self, alt_dir=''):
        suggestion = (
            os.path.splitext(os.path.basename(self.temp.puz_file))[0] +
            default_diag_ext)
        if alt_dir and not os.path.isabs(alt_dir):
            alt_dir = app_recent[alt_dir]    # retrieve directory from settings
        diag_file = \
            asksaveasfilename(defaultextension=default_diag_ext,
                              title='Save puzzle file',
                              initialdir=alt_dir or self.sess.puzzle_dir,
                              initialfile=suggestion)
        if not diag_file: return
        base, ext = os.path.splitext(diag_file)
        if not ext:
            diag_file = base + default_diag_ext
        self.temp.puz_file = diag_file
        new_latest_dir = os.path.dirname(diag_file)
        if new_latest_dir != self.sess.puzzle_dir:
            app_recent['latest_puzzle_dir'] = new_latest_dir
        self.save_file(1)

    def save(self, update_recent=0):
        if self.temp.puz_file in ('', new_puz_file):
            self.save_as()
        else:
            self.save_file(update_recent)

    def save_file(self, update_recent=0):
        base, ext = os.path.splitext(self.temp.puz_file)
        if ext != default_diag_ext:
            self.temp.puz_file = base + default_diag_ext
            self.eph.warnings['using_dg0_ext'] = (
                os.path.split(self.temp.puz_file)[1],
                os.path.split(base)[1] + ext)

        if self.temp.grid_pattern_up:
            # restore perm if only grid had been displayed; undo before
            # writing file to avoid losing information
            self.undo()

        try:
            ofile = open(self.temp.puz_file, 'wb')  # binary mode for pickling
        except EnvironmentError:
            user_dialog(showerror, *error_messages['invalid_save'])
            return
        ofile.write('%%Diagnil-%s\n' % version)
        full_perm = copy.deepcopy(self.perm)
        temp_to_perm(self.temp, full_perm)
        pickle.dump(full_perm, ofile, protocol=2)  # binary mode
        ofile.close()

        self.temp.needs_saving = 0
        self.temp.last_saved = copy.deepcopy(self.perm)
        self.gui.status_line['text'] = 'The puzzle has been saved.'
        self.update_window_title()
        time_text = \
            file_time_display(os.stat(self.temp.puz_file)[stat.ST_MTIME])
        self.eph.save_time_id = \
            update_msg_widget(self.gui.save_time_msg, time_text,
                              self.eph.save_time_id,
                              fg_color=msg_saved_color)
        if update_recent or app_recent['open_files'][0] != self.temp.puz_file:
            self.update_recent_list(self.temp.puz_file)    # do this at end

        self.emit_warnings()
        self.eph.warnings = {}


    def import_clues(self, from_file=1):
        if not self.clear(): return

        if from_file:
            file_types = [("Diagramless Clue Lists", ('*.txt',)),
                          ("All Files", "*")]
            initial_dir = app_recent['latest_clues_dir'] or home_directory
            clue_file = askopenfilename(filetypes=file_types,
                                        title='Open clue list file',
                                        initialdir=initial_dir)
            if not clue_file: return
            puz_content = ''
            app_recent['latest_clues_dir'] = os.path.dirname(clue_file)
        else:
            clue_file = ''
            try:
                puz_content = self.master.clipboard_get()
            except:
                puz_content = ''
            if not puz_content:
                user_dialog(showerror, *error_messages['no_clipboard_clues'])
                return
        self.temp = TempState()
        self.gui.configure_title_line('')
        self.new_puzzle_file()

        # reset menu items first in case load fails
        self.set_menu_item_state(DISABLED, *self.dynamic_menu_items)
        try:
            puz_defn = PuzzleDefn(clue_file, self.eph.warnings,
                                  semi_clueful=1, puz_content=puz_content)
        except FalseStart:
            self.new_clueless()
            return
        except IOError:
            user_dialog(showerror,
                        *error_msg_sub('corrupted_open_clues',
                                       os.path.basename(clue_file)))
            self.new_clueless()
            return
        except:       # most likely ill-formed clues
            user_dialog(showerror,
                        *error_msg_sub('open_unknown_variant',
                                       os.path.basename(clue_file)))
            self.new_clueless()
            return

        self.temp.puz_file = clue_file or new_puz_file
        self.temp.last_saved = self.perm     # until copy is made
        self.temp.puz_defn = puz_defn
        self.enter_clues(puz_defn)
        # use sess attribs, set temp.size_symm:
        self.set_puzzle_size(use_session=2)
        self.temp.puz_defn.width  = self.temp.size_symm[3]
        self.temp.puz_defn.height = self.temp.size_symm[4]
        self.temp.needs_saving = 1

        self.set_menu_item_state(NORMAL, *self.semi_clueful_menu_items)
        self.update_word_counts()
        self.update_window_title()
        self.show_main_grid()
        self.gui.puzzle_size['text'] = self.current_puzzle_size()
        eval_assertion(self.state_invariant, 'Post-installation check')


#    def download_selection(self):

#    def download_puz(self, url=''):


# To stay safe, we limit file deletions to puzzle files only.  Notify user
# and reject any files not having puzzle file extensions.  File contents
# are not checked, though.

    def delete(self):
        initial_dir = self.sess.puzzle_dir         # from user prefs
        file_types = [("Diagramless Puzzle Files", puz_file_ext),]
#                      ("All Files", "*")]
        paths = askopenfilenames(filetypes=file_types,
                                 title='Delete puzzle files',
                                 initialdir=initial_dir)
        if not paths: return
        puz_folder = os.path.split(os.path.split(paths[0])[0])[1]
        puz_ext = [ s[1:] for s in puz_file_ext ]
        selected_file_paths = [ (os.path.split(p)[1], p) for p in paths ]
        puz_file_paths = [ fp for fp in selected_file_paths
                           if os.path.splitext(fp[0])[1] in puz_ext ]
        non_puz_files = [ fp[0] for fp in selected_file_paths
                          if os.path.splitext(fp[0])[1] not in puz_ext ]
        if non_puz_files:
            title, message = error_messages['no_nonpuz_deletion']
            user_dialog(showerror, title,
                        message % (non_puz_files, puz_folder))
        if puz_file_paths:
            title, message = dialog_messages['confirm_delete']
            if user_dialog(askokcancel, title,
                           message % ([ fp[0] for fp in puz_file_paths ],
                                      puz_folder)):
                for fp in puz_file_paths: os.remove(fp[1])


    def exit(self, *events):
        self.sess.quitting += 1         # note an attempt in case of exceptions
        save_needed = self.need_to_save()
        if on_osx and save_needed:
            AE.AEInteractWithUser(50000000) # make user bring app to foreground
            self.master.update()            # ensure fully restored widgets
            ##### Issue: bringing app to foreground is flawed
        if self.sess.quitting > 1 or not save_needed \
               or self.ok_to_overwrite(0):
            delete_old_log_files()
            emit_log_file()
            emit_new_settings()
            if self.sess.trial_mode and \
               user_dialog(askokcancel,
                           *dialog_messages['delete_dg0_files']):
                # if user doesn't intend to keep using Diagnil, he can
                # accept the suggestion to delete the user_directory
                import shutil
                shutil.rmtree(user_directory, ignore_errors=1)
            try:
                self.master.destroy()
            except:            # sometimes have TclError on exit
                self.master.quit()
        else:
            self.sess.quitting -= 1           # user canceled quit attempt

    def show_file_properties(self):

        def show_properties(fr):
            ypad = 2
            pfr = Frame(fr)
            for r, prop_val in enumerate(self.collect_file_properties()):
                if prop_val:
                    pname  = Label(pfr, text=prop_val[0] + ':', font=bold_font)
                    pvalue = Label(pfr, text=prop_val[1], font=text_font,
                                   wraplength=300, justify=LEFT)
                    pname.grid(row=r, column=0, sticky=E, padx=10, pady=ypad)
                    pvalue.grid(row=r, column=1, sticky=W, padx=10, pady=ypad)
                else:
                    pname  = Label(pfr, text='', font=small_text)
                    pname.grid(row=r, column=0, sticky=E, padx=10, pady=ypad)
            pfr.pack(padx=20)
            Frame(fr).pack(pady=10)

        fr, widgets = positioned_dialog(self.master, [0], use_grab=on_win,
                                        dialog_proc=show_properties,
                                        width=0, height=0,
                                        title='Puzzle properties')


# ---------- Utility puzzle exporting ---------- #

# Pretty-print a Python user-defined class instance as a JSON-encoded file.
# Place each key/field on a new line.  Handle recursive object instances.

    def export_to_json(self):
        try:
            import json
        except ImportError:
            import simplejson as json    # for Python 2.5 case on Win XP

        perm_exp = copy.deepcopy(self.perm)
        temp_to_perm(self.temp, perm_exp)
        perm_exp.version = version

        suggestion = os.path.splitext(
                         os.path.basename(self.temp.puz_file))[0] + '.json'
        out_file = asksaveasfilename(defaultextension='.json',
                                     title='Export Diagnil .dg0 file to JSON',
                                     initialdir=default_puzzle_dir,
                                     initialfile=suggestion)
        if not out_file: return
        f_out = open(out_file, 'w')

        def emit_object(obj):
            obj_dict = getattr(obj, '__dict__', None)
            if obj_dict == None:
                raise ValueError, 'Top-level object not a class instance.'
            fields = obj_dict.items()
            fields.sort()
            punc = '{'
            for key, value in fields:
                print >> f_out, punc
                if hasattr(value, '__dict__'):
                    print >> f_out, '\n"%s":' % key ,
                    emit_object(value)
                    punc = ',\n'
                else:
                    print >> f_out, '"%s": ' % key, json.dumps(value) ,
                    punc = ','
            print >> f_out, '}' ,

        emit_object(perm_exp)
        print >> f_out, ''
        f_out.close()


# ---------- Edit menu commands ---------- #

# Undo (single step only) is currently handled by saving persistent
# puzzle state snapshots and rebuilding entire puzzle on a rollback.
# This is crude but acceptable for the amount of state and restoration
# involved.  On modest machines, though, this might be noticeably slow.
# Special case is finalized puzzle; reset final flag and rebuild puzzle.
# Another special case is if grid pattern has been displayed, which is
# treated like a regular undo except it must be recognized before the
# finalization step in case the grid display occurred after finalization.

# Undo/redo lists have items of the form:
#     (perm-state, nonperm-state, action-string).
# The string describes the transition that started in the state.

    def undo(self):
        def undone(redoable=1):
            for prev in reversed(self.temp.undo_state):
                del self.temp.undo_state[-1]
                if isinstance(prev[0], PermState):
                    if redoable:
                        self.temp.redo_state.append(
                            (copy.deepcopy(self.perm),
                             self.nonperm_recovery_state(),
                             prev[2]))
                    self.install_perm(prev[0], redo=1)
                    self.restore_nonperm(prev[1])
                    self.eph.action_string = prev[2]
                    return 1
                # shouldn't happen, but skip over any bad values of
                # undo state if encountered
            # no good ones left
            user_dialog(showerror, *error_messages['no_undo'])
            return 0    
            
        self.snap_wordbox_yview()
        if self.temp.grid_pattern_up:
            if undone(redoable=0):
                self.temp.grid_pattern_up = 0
                self.gui.status_line['text'] = \
                    '%s undoable actions remain.' % len(self.temp.undo_state)
        elif self.perm.final:
            restore_items = self.perm.final
            self.perm.final = ()
            self.gui.grids[0].delete('final')
            if self.temp.undo_state and \
                    self.temp.undo_state[-1][2].startswith('Finalize'):
                del self.temp.undo_state[-1]
            self.temp.redo_state.append((copy.deepcopy(self.perm),
                                         self.nonperm_recovery_state(),
                                         'Finalize Puzzle'))
            self.install_perm(self.perm, redo=1)
            self.restore_original_posns(*restore_items)
            self.set_grid_cursors(1 - self.sess.next_focus)
            self.gui.status_line['text'] = \
                'Undoing Finalize action. ' \
                'Previously completed puzzle may now be edited.'
            self.start_timer()
        elif undone():
            self.temp.multiword_selection = None
            self.gui.status_line['text'] = \
                'Undoing: %s.  %s undoable actions remain.' % \
                (self.eph.action_string, len(self.temp.undo_state))
        self.refresh_num_est()
        self.refresh_save_time_status()

    def redo(self):
        self.snap_wordbox_yview()
        if self.temp.redo_state:
            redo_tuple = self.temp.redo_state[-1]
            self.temp.undo_state.append((copy.deepcopy(self.perm),
                                         self.nonperm_recovery_state(),
                                         redo_tuple[2]))
            if redo_tuple[2].startswith('Finalize'):
                self.finalize_puzzle(redo_tuple[0].final, 0)
            else:
                self.install_perm(redo_tuple[0], redo=1)
                self.restore_nonperm(redo_tuple[1])
            del self.temp.redo_state[-1]
            self.temp.multiword_selection = None
            self.gui.status_line['text'] = \
                'Redoing: %s.  %s redoable actions remain.' % \
                (redo_tuple[2], len(self.temp.redo_state))
        else:
            user_dialog(showerror, *error_messages['no_redo'])
        self.refresh_num_est()
        self.refresh_save_time_status()
        self.check_if_done()


# Multistep sequences initiated using the popup context menu may be
# aborted from the main menu.  Grids are cleared of temporary objects,
# cursors are restored, and the state is restored as needed for the
# next command.  Temporary word displays and warning messages also
# are cleared.

    def abort_multistep(self, id=None):
        if self.eph.preview > 0:
            self.restore_state(id)
        else:
            self.close_action(*range(num_grids))
        self.eph.preview = 0
        self.restore_click_action()
        self.gui.status_line['text'] = 'Multistep sequence has been aborted.'


# Users may change some session settings via a dialog.
# New settings take effect immediately

    def change_session_settings(self):
        results = [0]
        var_dict = {}

        def apply_changes(fr):
            if not results[0]:
                return               # user canceled
            names = ('infer_nums', 'key_navigation', 'auto_complete')
            try:
                new_vals = [ var_dict[v][0].get() for v in names ]
                app_prefs['infer_nums'] = new_vals[0]
                self.sess.key_navigation = new_vals[1]
                self.change_key_nav_status(new_vals[1])
                app_prefs['auto_complete'] = new_vals[2]
            except FalseStart:
                pass     # error already displayed

        def get_settings(fr):
            title_text = 'Session Settings (changes take effect immediately)'
            Label(fr, text=title_text).pack(padx=20, pady=10)
            sfr = Frame(fr)
            self.sess_sett_dialog(sfr, var_dict)
            sfr.pack(pady=10, fill=X)
            Frame(fr).pack(fill=Y, expand=YES)

        fr, widgets = positioned_dialog(self.master, results,
                          use_cancel=1, use_grab=1, close_text='Apply',
                          dialog_proc=get_settings, width=0,
                          final_action=apply_changes,
                          title='Change Session Settings')

    def sess_sett_dialog(self, fr, var_dict):
        ident_fn = lambda v: v
        sett_fr = Frame(fr)
        for name, cur_val, parent, descrip in \
            (('infer_nums', app_prefs['infer_nums'], None,
              'Display word number estimates on grid'),
             ('key_navigation', self.sess.key_navigation, None,
              'Enable keystroke-based grid navigation'),
             ('auto_complete', app_prefs['auto_complete'], None,
              'Automatically check for puzzle completion (clueful mode)'),
             ) :
            var = BooleanVar()
            chfr = Frame(sett_fr)
            chkb = Checkbutton(chfr, variable=var, text=descrip)
            chkb.pack(side=LEFT)
            var.set(cur_val)
            chfr.pack(padx=5, pady=5, fill=X)
            var_dict[name] = (var, ident_fn, chkb, [])
            if parent: var_dict[parent][3].append((name, chkb))
            chkb['command'] = \
                lambda name=name: update_dependents(name, var_dict)
        sett_fr.pack(padx=10, pady=10, fill=X)


# Users may change preferences by editing a preference file via a
# dialog. New preferences take effect during the next session.

    def change_preferences(self):
        results = [0]

        def save_pref(fr):
            app_geometry['pref'] = fr.geometry()
            if not results[0]:
                return               # user canceled
            try:
                settings_file = os.path.join(user_directory, 'settings.py')
                update_prefs()       # => excep
                adjust_preferences()
                if self.sess.settings_time == os.path.getmtime(settings_file):
                    emit_new_settings()
                    self.gui.status_line['text'] = \
                        'New preferences have been saved.'
                    title, chg_msg = info_messages['prefs_changed']
                    msgs = [ '[ %s ]  %s' % (title, chg_msg) ]
                    log_user_message(title, chg_msg)
                    self.eph.temp_msg_id = \
                        show_temp_msg_panel(msgs, self.eph.temp_msg_id,
                                            self.gui.temp_msg_panel, 20, 10)
#                    user_dialog(showinfo, *info_messages['prefs_changed'])
                    self.sess.settings_time = os.path.getmtime(settings_file)
                else:
                    # timestamps differ => clashing edits
                    user_dialog(showerror,
                                *error_messages['settings_not_current'])
            except FalseStart:
                pass   # error message already displayed
                ### need to fix with validation proc

        # use a modal dialog to prevent inconsistent updates
        fr, widgets = positioned_dialog(self.master, results, top_pady=0,
                          use_cancel=1, use_grab=1, close_text='Save',
                          final_action=save_pref,
                          geometry=app_geometry['pref'],
                          title='Preferences for Diagnil')

        sett_fr = Frame(fr)
        update_prefs = self.display_preference_dialog(sett_fr)
        sett_fr.pack(pady=10, fill=X)
        Frame(fr).pack(fill=Y, expand=YES)


    def edit_imported_clues(self):
        sel = [ self.gui.wordbox[d].curselection() for d in (0,1) ]
        if filter(None, sel):
            dir, index = [ (d, int(s[0])) for d, s in zip((0,1), sel) if s ][0]
            sel_clue = (dir, self.temp.puz_defn.nums[dir][index],
                        self.temp.puz_defn.clues[dir][index])
        else:
            sel_clue = None

        results = [0, None, None, None]   # status, clue_str, dir, final_clue
        def get_clue(fr):
            label = 'Enter the number and text to edit or add a clue.\n' \
                    'To delete an existing clue, enter its number only.\n' \
                    'Note that modifying a clue cannot be undone.'
            Label(fr, text=label, justify=LEFT).pack(padx=20, pady=5)
            clue_var = StringVar()
            clue_entry = entry_widget(fr, width=50, textvariable=clue_var)
            clue_entry.pack(padx=15, pady=10)
            if sel_clue:
                clue_entry.insert(END, '%d %s' % sel_clue[1:])
            clue_entry.focus_set()
            results[1] = clue_var

            dir_var = IntVar()
            dir_fr = Frame(fr)
            for label, value in (('Across', 0), ('Down', 1)):
                radbut = Radiobutton(dir_fr, variable=dir_var,
                                     value=value, text=label)
                radbut.pack(side=LEFT, padx=10)
            dir_fr.pack(pady=5)
            if sel_clue: dir_var.set(sel_clue[0])
            else:        dir_var.set(0)
            results[2] = dir_var
            Frame(fr).pack(pady=10)

        num_only = re.compile('\s*(\d+)\s*')
        num_clue = re.compile('\s*(\d+)\s+(\S+.*)')
        def validate_clue(fr):
            clue_string = results[1].get()
            match = num_clue.match(clue_string)
            if match:
                if int(match.group(1)) > 0:
                    results[3] = (results[2].get(), int(match.group(1)),
                                  match.group(2).strip())   # (dir, num, text)
                    return results[3]
                else:
                    user_dialog(showerror, *error_messages['bad_clue_form'])
                    return None
            match = num_only.match(clue_string)
            if match:
                dir, num = results[2].get(), int(match.group(1))
                if num in self.temp.puz_defn.nums[dir]:
                    results[3] = (dir, num, '')
                    return results[3]
                else:
                    user_dialog(showerror,
                                *error_msg_sub('bad_clue_number', num))
            else:
                user_dialog(showerror, *error_messages['bad_clue_form'])
            return None
        def update_clues(fr):
            if not results[0]:   # user canceled
                return
            # make changes after dialog closes
            self.master.after(100, self.edit_puz_defn, *results[3])

        fr, widgets = positioned_dialog(
                          self.master, results, top_pady=0, use_grab=1,
                          use_cancel=1, close_text='Apply', width=0,
                          dialog_proc=get_clue, final_action=update_clues,
                          validation_proc=validate_clue,
                          title='Edit Imported Clues')

    def edit_puz_defn(self, dir, num, text):
        # Only puz_defn objects need changing. New clues will not
        # have numbered items in perm objects.
        try:
            index = self.temp.puz_defn.nums[dir].index(num)   ## excep
            if text:
                self.temp.puz_defn.clues[dir][index] = text
            else:
                del self.temp.puz_defn.nums[dir][index]
                del self.temp.puz_defn.clues[dir][index]
        except ValueError:
            # new clue number => insert in order
            index = bisect_left(self.temp.puz_defn.nums[dir], num)
            self.temp.puz_defn.nums[dir].insert(index, num)
            self.temp.puz_defn.clues[dir].insert(index, text)
        self.save()
        self.open_puz(puz_file=self.temp.puz_file)


# ---------- View menu commands ---------- #

# Users may declare the puzzle size for displaying out-of-bounds region.

    def declare_puzzle_size(self, use_session=0):
        results = [0]
        var_dict = {}

        def apply_decl(fr):
            if not results[0]:
                return               # user canceled
            try:
                current = self.temp.size_symm
                self.set_puzzle_size(use_session,
                                     *[ var_dict[v][0].get() for v in
                                        ('show_boundary', 'apply_symmetry',
                                         'symmetry_type',
                                         'puzzle_width', 'puzzle_height') ])
                if not use_session and self.temp.size_symm[1]:
                    self.add_symmetric_blocks()
                self.temp.needs_saving = current != self.temp.size_symm
                self.update_window_title()
                self.emit_warnings()
                self.eph.warnings = {}
            except FalseStart:
                pass     # error already displayed

        def get_puz_size(fr):
            title_text = 'Set Puzzle Dimensions and Symmetry Attributes'
            Label(fr, text=title_text).pack(pady=10)
            sfr = Frame(fr)
            self.size_symm_dialog(sfr, use_session, var_dict)
            sfr.pack(pady=10, fill=X)
            Frame(fr).pack(fill=Y, expand=YES)

        fr, widgets = positioned_dialog(self.master, results, top_pady=2,
                          use_cancel=1, use_grab=1, close_text='Apply',
                          dialog_proc=get_puz_size, width=0,
                          final_action=apply_decl,
                          title='Declare Puzzle Size')

    def size_symm_dialog(self, fr, use_session, var_dict):
        ident_fn = lambda v: v
        if use_session:
            cur_boundary, cur_symm, cur_type, cur_width, cur_height = \
                (self.sess.show_boundary, self.sess.apply_symmetry,
                 self.sess.symmetry_type,
                 self.sess.puzzle_width, self.sess.puzzle_height)
        elif self.temp.size_symm:
            cur_boundary, cur_symm, cur_type, cur_width, cur_height = \
                self.temp.size_symm
            # account for asymmetric designs (type = None):
            cur_symm = cur_type and cur_symm or 0 # no strings for BooleanVar
        else:
            cur_boundary, cur_symm, cur_type, cur_width, cur_height = \
                (0, 0, 'rot', 0, 0)

        sett_fr = Frame(fr)
        for name, cur_val, parent, descrip in \
            (('show_boundary', cur_boundary, None,
              'Use size below and show bounded puzzle region'),
             ('apply_symmetry', cur_symm, 'show_boundary',
              'Show black squares implied by symmetry (when size given):'),
             ) :
            var = BooleanVar()
            chfr = Frame(sett_fr)
            chkb = Checkbutton(chfr, variable=var, text=descrip)
            chkb.pack(side=LEFT)
            var.set(cur_val)
            chfr.pack(padx=5, pady=5, fill=X)
            var_dict[name] = (var, ident_fn, chkb, [])
            if parent: var_dict[parent][3].append((name, chkb))
            chkb['command'] = \
                lambda name=name: update_dependents(name, var_dict)
        sett_fr.pack(padx=10, pady=0, fill=X)

        var = StringVar()
        for radio_list in ((('Rotational', 'rot'),
                            ('Horizontal', 'horiz'),
                            ('Vertical', 'vert')),
                           (('Diagonal, UL-LR', 'ul-lr'),
                            ('Diagonal, UR-LL', 'ur-ll'))):
            sett_fr = Frame(fr)
            for label, key in radio_list:
                radbut = Radiobutton(sett_fr, variable=var,
                                     value=key, text=label)
                radbut.pack(side=LEFT, padx=5)
                var_dict['apply_symmetry'][3].append((None, radbut))
            sett_fr.pack(padx=40, pady=2, fill=X)
        var.set(cur_type)
        var_dict['symmetry_type'] = (var, ident_fn, None, [])
        Frame(fr).pack(pady=5)

        size_fr = Frame(fr)
        label = Label(size_fr, text='Current puzzle size:')
        label.pack(side=LEFT)
        var_dict['show_boundary'][3].append((None, label))
        size_fr.pack(padx=15, pady=5, fill=X)

        size_fr = Frame(fr)
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
            if (cur_width, cur_height) == (v, v):
                var.set(v)
        size_fr.pack(padx=40, pady=2, fill=X)

        size_fr = Frame(fr)
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
                    (cur_width, cur_height),
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

        size_fr.pack(padx=40, pady=2, fill=X)
        update_dependents('show_boundary', var_dict)


# Display the grid pattern (black squares) only without words.
# Implemented as a step so user can just undo to restore normal view.
# Applies to main grid only.

    def view_grid_pattern(self):
        if self.temp.grid_pattern_up:  # pattern already displayed
            return                     # no need for error message

        self.start_action(override_final=1)            # make it undoable
        all_blocks = copy.deepcopy(self.perm.blocks)
        blocks = all_blocks[0]
        final = self.perm.final
        row0, col0, wid, ht = self.current_puzzle_size(text_form=0)

        # collect end blocks from current state
        for row, row_cells in enumerate(self.aux.cells[0]):
            for col, cell in enumerate(row_cells):
                if cell[2]:
                    blocks[(row, col)] = 1
        if final:
            # mark empty cells within grid for filling
            for row, row_cells in enumerate(self.aux.cells[0][:ht]):
                for col, cell in enumerate(row_cells[:wid]):
                    if cell == null_cell:
                        blocks[(row, col)] = 1
        self.clear(0)

        # Use a yellow background around region of current puzzle
        # plus a thick blue line on the border.
        limit = grid_size[0] * cell_size + 1
        x0, y0 = col0 * cell_size, row0 * cell_size
        x1, y1 = x0 + wid * cell_size, y0 + ht * cell_size
        self.gui.grids[0].create_polygon(x0, y0, x1, y0,
                                         x1, y1, x0, y1,
                                         fill=word_bg_color,
                                         tags=('final',))
        self.perm.blocks = all_blocks
        self.place_blocks(self.perm)

        # Paint four strips of light yellow around grid.
        strips = ((0, 0, limit, y0 - 2), (0, 0, x0 - 2, limit),
                  (x1 + 2, 0, limit, limit), (0, y1 + 2, limit, limit),)
        for sx0, sy0, sx1, sy1 in strips:
            self.gui.grids[0].create_polygon(sx0, sy0, sx1, sy0,
                                             sx1, sy1, sx0, sy1,
                                             outline='', fill=outer_bg_color,
                                             tags=('final',))

        self.gui.grids[0].create_line(x0+1, y0+1, x1+1, y0+1,
                                      x1+1, y1+1, x0+1, y1+1, x0+1, y0+1,
                                      fill='dark blue', width=3,
                                      tags=('final',))
        self.gui.grids[0].create_text(max(150, (x0 + x1)//2), y1 + 60,
                                      text='Select Undo to restore words.',
                                      font=heading2_font,
                                      fill='dark blue', tags=('final',))

        self.temp.multiword_selection = None
        self.temp.grid_pattern_up = 1
        self.gui.status_line['text'] = \
            'Grid pattern displayed; undo to restore words.'
        self.save_action_string('Display Grid Pattern')
        self.perm.final = final
        self.finish_action(None, None)


# Show list of error and warning messages in a separate window.
# Position at end of list (most recent).

    def show_puzzle_notes(self):
        if self.temp.puz_defn:
            label = self.puz_file_name()
            notes_lines = self.temp.puz_defn.notes
        else:
            label = ''
            notes_lines = ('This puzzle was not distributed in '
                           'electronic form and therefore has no notes.')
        def show_notes(fr):
            if label:
                Label(fr, text=label, font=text_font).pack(pady=5)
            tfr, txt = scrolled_text_widget(fr, width=40, height=10,
                                            padx=5, pady=5)
            for line in notes_lines:
                txt.insert(END, line)
            txt['state'] = DISABLED
            tfr.pack(padx=10, pady=5, fill=BOTH, expand=YES)
            Frame(fr, width=0, height=0).pack(pady=5)

        fr, widgets = positioned_dialog(self.master, [0], top_pady=2,
                                        dialog_proc=show_notes, width=0,
                                        title='Puzzle notes', use_grab=on_win)

# Show across and down clues in a separate window with normal size font.
# Use two narrow columns.

    def show_clues_window(self):
        puz_defn = self.temp.puz_defn
        if puz_defn:
            title_string = 'Clues for %s' % self.puz_file_name()
        else:
            user_dialog(showerror, *error_messages['no_clues_available'])
            return

        def show_clues(fr):
            for dir in 0,1:
                tfr, txt = scrolled_text_widget(
                           fr, width=30, height=40, wrap=WORD, # relief=FLAT,
                           font=text_font, padx=5, pady=5,
                           highlightthickness=0, background=text_bg_color)
                txt.insert(END, '%s\n\n' % dir_text[dir])
                for num, clue in zip(puz_defn.nums[dir], puz_defn.clues[dir]):
                    txt.insert(END, '%2d.  %s\n' % (num, clue))
                txt.tag_add('all_lines', 1.0, END)
                txt.tag_configure('all_lines', lmargin2=30)
                txt['state'] = DISABLED
                tfr.pack(padx=5, pady=5, side=LEFT, fill=BOTH, expand=YES)
            return txt

        fr, widgets = positioned_dialog(self.master, [0], width=0, height=0,
                                        dialog_proc=show_clues, top_pady=0,
                                        title=title_string)

    def show_selected_clues(self):
        puz_defn = self.temp.puz_defn
        if puz_defn:
            title = 'Clues for %s' % self.puz_file_name()
        else:
            user_dialog(showerror, *error_messages['no_clues_available'])
            return

        sel = [ self.gui.wordbox[d].curselection() for d in (0,1) ]
        if not filter(None, sel):
            user_dialog(showerror, *error_messages['select_displayable'])
            return None
        rev = [ (s[0], d) for s, d in zip(sel, (0,1)) if s ]
        num_dir_clue = [ (int(self.gui.wordbox[d].get(i)[0][0]),
                          dir_text[d],
                          self.temp.puz_defn.clues[d][i])
                         for i, d in rev ]
        message = '\n'.join([ u'%d-%s:  %s' % ndc for ndc in num_dir_clue ])
        user_dialog(showinfo, title, message)
        for i, dir in rev:
            self.clear_wordbox_selection(dir)


# Show list of undo/redo actions in a separate window.
# Position at end of list (most recent).

    def show_undo_redo_list(self):
        def add_buttons(fr):
            buttons = ((close_button_text, lambda : close_msg_list()),
                       ('Refresh', lambda : show_all()))
            but_fr, widgets = button_row(fr, buttons)
            but_fr.pack(fill=X, padx=20, pady=4, side=BOTTOM)
        top, txt = scrolled_text_display(
                       title='Undo/Redo Actions',
                       geometry=app_geometry['msg_list'],
                       button_proc=add_buttons)
        def show_all():
            txt['state'] = NORMAL
            txt.delete(1.0, END)
            txt.insert(END, 'Undoable actions:\n\n')
            action_list = [ (n+1, s[-1]) for n,s in
                            enumerate(reversed(self.temp.undo_state)) ]
            for num_action in reversed(action_list):
                txt.insert(END, '%s.  %s\n' % (num_action))
            txt.insert(END, '\n==============\n\nRedoable actions:\n\n')
            action_list = [ (n+1, s[-1]) for n,s in
                            enumerate(reversed(self.temp.redo_state)) ]
            for num_action in action_list:
                txt.insert(END, '%s.  %s\n' % (num_action))
            txt['state'] = DISABLED
        def close_msg_list(*args):
            app_geometry['msg_list'] = top.geometry()
            top.destroy()
        wrapped_bind(top, '<Return>', close_msg_list)
        top.protocol('WM_DELETE_WINDOW', close_msg_list)
        show_all()

# Show list of error and warning messages in a separate window.
# Position at end of list (most recent).

    def show_message_list(self):
        def add_buttons(fr):
            buttons = ((close_button_text, lambda : close_msg_list()),
                       ('Refresh', lambda : show_all()),
                       ('Clear List', lambda : clear_all()))
            but_fr, widgets = button_row(fr, buttons)
            but_fr.pack(fill=X, padx=20, pady=4, side=BOTTOM)
        top, txt = scrolled_text_display(
                       title='Recent Diagnil Messages',
                       geometry=app_geometry['msg_list'],
                       button_proc=add_buttons)
        def clear_all():
            txt['state'] = NORMAL
            reset_user_message_log()
            txt.delete(1.0, END)
            txt['state'] = DISABLED
        def show_all():
            txt['state'] = NORMAL
            txt.delete(1.0, END)
            for v in user_message_log: txt.insert(END, v)
            txt.insert(END, 'Total of %d entries\n' % len(user_message_log))
            txt.yview_moveto(1.0)
            txt['state'] = DISABLED
        def close_msg_list(*args):
            app_geometry['msg_list'] = top.geometry()
            top.destroy()
        wrapped_bind(top, '<Return>', close_msg_list)
        top.protocol('WM_DELETE_WINDOW', close_msg_list)
        show_all()


# ---------- Solution menu commands ---------- #

    def first_square_hint(self):
        # The position of the first across word should always be
        # available in clueful mode.
        try:
            row, col = self.temp.puz_defn.soln_posns[0][1]
        except:
            user_dialog(showerror, *error_messages['no_puz_defn'])
            return None
        user_dialog(showinfo, 'First square hint',
                    'The first square of 1-Across is the box at '
                    'row %d, column %d.' % (row+1, col+1))


    def revealable(self, check_selection=1):
        if not self.temp.puz_defn:
            user_dialog(showerror, *error_messages['no_puz_defn'])
            return None
        if self.temp.puz_defn.soln_flags:
            user_dialog(showerror, *error_messages['solution_locked'])
            return None
        if not check_selection: return 1

        sel = [ self.gui.wordbox[d].curselection() for d in (0,1) ]
        rev = [ (s[0], d) for s, d in zip(sel, (0,1)) if s ]
        if not rev:
            user_dialog(showerror, *error_messages['select_revealable'])
            return None
        if len(rev) > 1:
            user_dialog(showerror, *error_messages['both_revealable'])
            return None
        return rev[0]

    def check_soln_word(self):
        revealable = self.revealable()
        if revealable == None: return
        sel, dir = revealable
        num = int(self.gui.wordbox[dir].get(sel)[0][0])
        word = self.perm.words[dir].get(num)
        if word == None:
            user_dialog(showerror, *error_messages['selection_unentered'])
            return None

        word = word.upper()
        soln_word = self.temp.puz_defn.soln_words[dir][num]
        if word == soln_word:
            ending = 'the CORRECT letters'
        elif len(word) == len(soln_word):
            masked = [ (word[i] != soln_word[i] and '?') or word[i]
                       for i in range(len(word)) ]
            ending = 'some WRONG letters: %s' % ''.join(masked)
        else:
            ending = 'the WRONG length'
        user_dialog(showinfo, 'Check word',
                    self.puz_file_name() +                    
                    '\n\nWord %s %s has %s.\n' % (num, dir_text[dir], ending))
        self.clear_wordbox_selection(dir)

    def check_soln_posn(self):
        revealable = self.revealable()
        if revealable == None: return
        sel, dir = revealable
        num = int(self.gui.wordbox[dir].get(sel)[0][0])
        posn = self.perm.posns[0][dir].get(num)
        if posn == None:
            user_dialog(showerror, *error_messages['selection_ungridded'])
            return None

        if posn == self.temp.puz_defn.soln_posns[dir][num]:
            outcome = 'CORRECT'
        else:
            outcome = 'WRONG'
        user_dialog(showinfo, 'Check word',
                    self.puz_file_name() +                    
                    '\n\nWord %s %s is in the %s position.\n' %
                    (num, dir_text[dir], outcome))
        self.clear_wordbox_selection(dir)

    def check_solution(self, finalize=0, row_offset=None, col_offset=None,
                       auto_check=0):
        # In the finalize case, we want the following check to warn
        # about locked solutions, but we proceed anyway.
        if self.revealable(check_selection=0) == None and not finalize:
            return

        words = self.perm.words
        posns = self.perm.posns[0]    # check grid 0 only
        soln_words = self.temp.puz_defn.soln_words
        soln_posns = self.temp.puz_defn.soln_posns
        if row_offset == None:
            if posns[0]:
                across_posns = posns[0].values()
                row_offset = min([ p[0] for p in across_posns ])
                col_offset = min([ p[1] for p in across_posns ])
            elif posns[1]:
                down_posns = posns[1].values()
                row_offset = min([ p[0] for p in down_posns ])
                col_offset = min([ p[1] for p in down_posns ])
            else:
                row_offset, col_offset = 0, 0

        errors = ([], [])
        for dir in (0,1):
            soln_nums = soln_words[dir].keys()
            for num in soln_nums:
                word = words[dir].get(num)
                row_col = posns[dir].get(num)
                if row_col:
                    posn = (row_col[0] - row_offset, row_col[1] - col_offset)
                    if (word and word.upper()) != soln_words[dir][num] or \
                            posn != soln_posns[dir][num] :
                        errors[dir].append(num)
                else:
                    errors[dir].append(num)

        if filter(None, errors):
            if auto_check: return 0     # check after full word count
            outcome = self.puz_file_name() + \
                      '\n\nYour solution is not fully correct.'
            for dir in (0,1):
                if errors[dir]:
                    errs = '\n\nThe following %s words have errors ' \
                           'or have yet to be entered: %s.' % \
                           (dir_text[dir], str(errors[dir])[1:-1])
                    outcome = outcome + errs
            user_dialog(showinfo, 'Check solution', outcome)
            return 0
        elif finalize:
            return 1
        else:
            if row_offset + col_offset > 0:
                qualification = ' (allowing for row and column offsets)'
            else:
                qualification = ''
            outcome = 'Congratulations! Your solution is 100%% correct%s.\n' \
                      % qualification
            user_dialog(showinfo, 'Check solution', outcome)
            return 1

    def reveal_soln_word(self):
        revealable = self.revealable()
        if revealable == None: return
        sel, dir = revealable
        num = int(self.gui.wordbox[dir].get(sel)[0][0])
        word = self.temp.puz_defn.soln_words[dir].get(num)
        if word == None:
            user_dialog(showerror, *error_messages['selection_unentered'])
            return None
        user_dialog(showinfo, 'Reveal word',
                    self.puz_file_name() + '\n\nWord %s %s is %s.\n' %
                    (num, dir_text[dir], word.upper()))
        self.clear_wordbox_selection(dir)

    def reveal_soln_posn(self):
        revealable = self.revealable()
        if revealable == None: return
        sel, dir = revealable
        num = int(self.gui.wordbox[dir].get(sel)[0][0])
        posn = self.temp.puz_defn.soln_posns[dir].get(num)
        if posn == None:
            user_dialog(showerror, *error_messages['selection_ungridded'])
            return None
        user_dialog(showinfo, 'Reveal word',
                    self.puz_file_name() + 
                    '\n\nWord %s %s starts in cell (%d, %d).\n' %
                    (num, dir_text[dir], 1+posn[0], 1+posn[1]))
        self.clear_wordbox_selection(dir)

    def reveal_solution(self):
        if not (self.revealable(check_selection=0) and
                user_dialog(askokcancel,
                            *dialog_messages['confirm_revelation']) and
                self.ok_to_overwrite()):
            return

        def const_dict(nums, v):
            d = {}
            for n in nums: d[n] = v
            return d

        puz = self.temp.puz_defn
        if not puz: return
        perm = PermState()
        perm.nums  = copy.deepcopy(puz.nums)

        perm.words = [None, None]
        use_upper = app_prefs['upper_case']
        for dir in 0,1:
            words = {}
            for n, w in puz.soln_words[dir].items():
                if use_upper: words[n] = w.upper()
                else:         words[n] = w.lower()
            perm.words[dir] = words

        perm.posns[0] = copy.deepcopy(puz.soln_posns)
        perm.grid_id = [ const_dict(nums, 0) for nums in perm.nums ]

        self.start_action()             # make it undoable
        self.install_perm(perm)
        self.temp.revealed = 1          # extra attribute (as of 2.3)
        self.temp.multiword_selection = None
        self.gui.status_line['text'] = \
            'Complete puzzle solution has been revealed.'
        self.save_action_string('Reveal Solution')
        self.finish_action(None, None)

    def unlock_solution(self):
        if not self.temp.puz_defn:
            user_dialog(showerror, *error_messages['no_puz_defn'])
            return
        if not self.temp.puz_defn.soln_flags:
            user_dialog(showinfo, *info_messages['already_unlocked'])
            return

        results = [0, None, None]
        def get_soln_key(fr):
            label = 'Enter the four-digit key to unlock the solution:'
            Label(fr, text=label).pack(padx=20, pady=10)
            key_var = StringVar()
            key_entry = entry_widget(fr, width=6, textvariable=key_var)
            # if using_ttk or using_tile:
            #     key_entry = Entry(fr, width=6, textvariable=key_var)
            # else:
            #     key_entry = Entry(fr, width=6, highlightthickness=2,
            #                       background=text_bg_color, relief=SUNKEN,
            #                       highlightcolor=highlight_color,
            #                       textvariable=key_var)
            key_entry.pack(pady=20)
            key_entry.focus_set()
            results[1] = key_var
        def validate_key(fr):
            key_string = results[1].get()
            if len(key_string) == 4 and key_string.isdigit():
                results[2] = map(int, list(key_string))
            else:
                results[2] = None
                user_dialog(showerror,
                            *error_msg_sub('bad_key_digits', key_string))
            return results[2]
        def unlock_soln(fr):
            if not results[0]:   # user canceled
                return
            elif results[2]:
                try:
                    self.temp.puz_defn.unlock_solution(results[2])
                    self.set_menu_item_state(NORMAL, *self.solution_menu_items)
                    self.set_menu_item_state(DISABLED, 'Unlock Solution...')
                except KeyError:
                    user_dialog(showerror,
                                *error_msg_sub('bad_solution_key',
                                               results[1].get()))
                except ValueError:
                    user_dialog(showerror,
                                *error_messages['unscrambling_error'])
            else:
                pass    # user input validation ensures a key or cancellation

        fr, widgets = positioned_dialog(self.master, results, use_grab=1,
                                        use_cancel=1, close_text='Unlock',
                                        dialog_proc=get_soln_key,
                                        validation_proc=validate_key,
                                        final_action=unlock_soln, width=0,
                                        title='Unlock Puzzle Solution')


# ---------- Help menu commands ---------- #

# Quick Start and User's guides are imported and displayed in
# scrolling text widgets.

    def short_help_dialog(self, title, body, tab_stops):
        def show_text(fr):
            tfr, txt = scrolled_text_widget(fr, width=70, tab_stops=tab_stops)
            tfr.pack(padx=5, pady=0)
#            tfr.bind('<Enter>', lambda event: txt.focus_set())
            return tfr, txt

        if on_osx: geometry='+50+50'
        else:      geometry='+50+0'
        fr, widgets = positioned_dialog(self.master, [0], top_pady=0,
                                        geometry=geometry,  title=title,
                                        dialog_proc=show_text)
        header_text = 'Diagnil: Diagramless Crossword ' \
                      'Assistant   			  Version %s\n'
        widgets[1].insert(END, header_text % version)
        help_insert_items(body, widgets[1])
        widgets[1]['state'] = DISABLED

    def quick_start(self):
        import diag_quick
        self.short_help_dialog('Quick Start Guide for Diagnil',
                               diag_quick.quick_text,
                               ('.5c','numeric','1c',
                                '8c','numeric','8.5c','10c'))

    def diagramless_primer(self):
        import diag_primer
        self.short_help_dialog('Primer on Diagramless Solving',
                               diag_primer.primer_text,
                               ('.5c','numeric','1c',
                                '6c','numeric','6.5c','8c'))

    def help(self):
        show_users_guide(self.master)

    def view_samples(self):
        self.open_puz(alt_dir=sample_puzzle_dir)

    def about(self):
        def show_about(fr):
            title_row = Frame(fr)
            self.sess.icon = \
                PhotoImage(file=os.path.join(base_directory, 'dg0-128.gif'))
            Label(title_row, image=self.sess.icon).pack(padx=20, side=LEFT)
            right_side = Frame(title_row)
            Label(right_side, text='Diagnil',
                  font=heading2_font).pack(pady=10)
            Label(right_side, justify=CENTER, text=_about_text_1,
                  font=text_font).pack(pady=10)
            right_side.pack(padx=20, side=LEFT)
            title_row.pack(padx=10, pady=10)
            Message(fr, justify=CENTER, text=_about_text_2,
                    font=text_font, aspect=400).pack(padx=20)

        fr, widgets = positioned_dialog(self.master, [0], width=0,
                                        dialog_proc=show_about,
                                        title='About Diagnil', use_grab=on_win)


# --------- Special button/menu item handlers --------- #

    def swap_grids(self):
        self.master.after_cancel(self.eph.visit_id)
        if on_osx and self.sess.focus_region >= 2:
            # Canvas Leave bindings don't fire on OS X when swapping
            from_id = self.sess.focus_region - 2
            self.gui.leave_grid[from_id]()
        if self.sess.current_grid:
            self.gui.mini_frame.lower(self.gui.main_grid)
        else:
            self.gui.mini_frame.tkraise(self.gui.main_grid)
        self.sess.current_grid = 1 - self.sess.current_grid
        dir = 1 - self.sess.next_focus
        self.gui.word_ent[dir].focus_set()
        if on_osx:
            # Canvas Enter bindings don't fire on OS X when swapping
            location = self.find_grid_cell()
            if location:
                grid, id, row, col = location
                grid.delete('visit')
                self.gui.enter_grid[id]()

    def show_main_grid(self):
        if self.sess.current_grid:
            self.gui.mini_frame.lower(self.gui.main_grid)
            self.sess.current_grid = 0

    def toggle_entry_focus(self, location=None):
        dir = self.sess.next_focus
        self.gui.toggle_focus_proc[dir]()
        self.eph.prev_posn = -1,-1
        location = location or self.find_grid_cell()
        if location:
            self.clear_listbox_indicator(1-dir)
            if self.sess.key_navigation:
                grid, id, row, col = location
                self.set_key_cursor(self.temp.key_cursors[id][1:3])
            else:
                self.adjust_word_number(dir, 0, delay_factor=1)
            self.move_quiescent(*location[1:])

    def toggle_key_nav_mode(self):
        if self.sess.key_navigation:
            for id in range(num_grids):
                self.gui.grids[id].delete('infer2')
                self.gui.grids[id].delete('key_cursor')
            self.sess.key_navigation = 0
        else:
            for id in range(num_grids):
                self.set_key_cursor(self.temp.key_cursors[id][1:3])
            self.sess.key_navigation = 1


# Insert the last num,word into entry widget, or recall existing
# word if number supplied.

    def recall_last(self):
        dir = 1 - self.sess.next_focus
        last = self.eph.last_word[dir]
        if last:
            num, word = last
        else:
            user_dialog(showerror, *error_messages['cannot_recall_arb'])
            return
        self.temp.sel_num_word[dir] = (num, word, None)
        self.gui.word_ent[dir].delete(0, END)
        current_text = '%d %s' % (num, word)
        self.gui.word_ent[dir].insert(0, current_text)
        self.sess.word_entry_text[dir] = current_text
        self.gui.next_num[dir]['text'] = ''

        id = self.sess.focus_region - 2
        if id < 0: return    # not over a grid
        try:
            self.set_key_cursor(posn=self.perm.posns[id][dir][num])
        except IndexError:
            pass           # word not pasted on grid
        self.gui.grids[id].delete('infer')
        self.gui.grids[id].delete('infer2')
        self.gui.grids[id].delete('visit')


# Word search pops up a toplevel window, then collects a word list from
# current word items (with acquired letters) in the listbox.

    def search_for_word(self, dir=None):
        if dir == None: dir = 1 - self.sess.next_focus
        search_panel, start_proc, slide_proc = self.gui.search_panels[dir]
        location = self.find_grid_cell()
        if location:
            grids = self.gui.grid_area
            if self.sess.key_navigation:
                id = location[1]
                row, col = self.temp.key_cursors[id][1:3]
                start_args = (id, row, col)
                # try to keep window away from area of user's interest
                if id % 2 == 1 : relx = 1    # left-side minigrids
                elif id > 0:     relx = 0    # right-side minigrids
                else:
                    x = col * cell_size - self.gui.grids[id].canvasx(0)
                    if float(x) / grids.winfo_width() > 0.4 : relx = 0
                    else:                                     relx = 1
            else:
                x = grids.winfo_pointerx() - grids.winfo_rootx()
                # try to keep window away from area of user's interest
                if float(x) / grids.winfo_width() > 0.4 : relx = 0
                else:                                     relx = 1
                start_args = location[1:]
        else:
            relx = 1
            start_args = ()
        slide_proc(relx)
        start_proc(None, start_args)


# Collect information on file properties.  Returns a list of the
# form [(prop, value), ...].

    def collect_file_properties(self):
        pfile = self.temp.puz_file
        file_ext = os.path.splitext(pfile)[1].lower()
        file_type = (
            file_ext == default_diag_ext and 'Diagnil puzzle file' or
            file_ext in default_puz_ext and 'Across Lite puzzle file' or
            file_ext in default_xpf_ext and 'XPF puzzle file' or
            file_ext in default_jpz_ext and 'Crossword Compiler puzzle file' or
            file_ext in default_ipuz_ext and 'ipuz puzzle file' or
            file_ext == '.txt' and 'Scanned clue lists' or
            pfile and 'Unsupported file type' or
            'New puzzle (no file yet)' )
        puz_defn = self.temp.puz_defn
        puzzle_type = ''
        soln_presence = 'Unavailable'
        if puz_defn:
            if puz_defn.format_type == 'ipuz':
                orig_attribs = ('ipuz puzzle file', puz_defn.editor,
                                puz_defn.publisher, puz_defn.date)
                if puz_defn.soln_words: soln_presence = 'Included'
                puzzle_type = puz_defn.puzzle_type.capitalize() or 'Regular'
            elif puz_defn.format_type == 'xpf':
                orig_attribs = ('XPF puzzle file', puz_defn.editor,
                                puz_defn.publisher, puz_defn.date)
                soln_presence = 'Included'
                puzzle_type = puz_defn.puzzle_type.capitalize() or 'Regular'
            elif puz_defn.format_type == 'jpz':
                orig_attribs = ('Crossword Compiler puzzle file',
                                puz_defn.editor, puz_defn.publisher,
                                puz_defn.date)
                soln_presence = 'Included'
                puzzle_type = puz_defn.puzzle_type.capitalize() or 'Regular'
            elif puz_defn.format_type == 'puz':
                orig_attribs = ('Across Lite puzzle file', '', '', '')
                if puz_defn.soln_flags: soln_presence = 'Locked'
                else:                   soln_presence = 'Included'
                if puz_defn.black == ':': puzzle_type = 'Diagramless'
                else:                     puzzle_type = 'Regular'
            elif puz_defn.format_type == 'scanned':
                orig_attribs = ('Scanned clue lists', '', '', '')
        else:
            orig_attribs = ('None (clueless mode)', '', '', '')
        if orig_attribs[0] == file_type: imported_from = ''
        else:                            imported_from = orig_attribs[0]

        mod_time = pfile and \
                   time.asctime(time.localtime(os.path.getmtime(pfile)))
        flen = pfile and os.path.getsize(pfile) or 0
        file_size = '%.1f KB (%d bytes)' % (flen / 1000.0, flen)
        a_nums, d_nums = self.perm.nums
        word_counts = len(a_nums), len(d_nums)
        if self.temp.revealed:
            status = 'Solution revealed'
        elif self.perm.final and self.temp.puz_defn and \
                self.temp.puz_defn.soln_words:
            if self.temp.puz_defn.soln_flags:
                # locked solution; unchecked
                status = 'Complete (%d, %d words)' % word_counts
            else:
                status = 'Complete, checked (%d, %d words)' % word_counts
        elif self.perm.final:
            status = 'Complete (%d, %d words)' % word_counts
        elif a_nums or d_nums:
            status = 'Unfinished (%d, %d words)' % word_counts
        else:
            status = 'Unattempted'
        solving_time = timer_display(self.temp.solv_time)

        return ( ('File name',          os.path.basename(pfile)),
                 ('File type',          file_type),
                 ('Imported from',      imported_from),
                 ('Location',           os.path.split(pfile)[0]),
                 ('Last saved',         mod_time),
                 ('File size',          file_size),
                 None,
                 ('Puzzle type',        puzzle_type),
                 ('Puzzle editor',      orig_attribs[1]),
                 ('Publisher',          orig_attribs[2]),
                 ('Publication date',   orig_attribs[3]),
                 ("Author's solution",  soln_presence),
                 ('Solving status',     status),
                 ('Solving time',       solving_time),
                 )

# ---------- End of class DiagCommand ---------- #


# ---------- Download procedures ---------- #

# Under development. Might appear in a future version.


# ---------- Utility procedures ---------- #

# The format_type attribute wasn't introduced until version 2.4,
# nor was the ipuz file format.
# This function tries to infer the type from older .dg0 files.

def determine_format_type(puz_defn):
    if hasattr(puz_defn, 'date'): return 'xpf'
    elif puz_defn.soln_grid:      return 'puz'
    else:                         return 'scanned'


def compress_path(path):
    elements = string.split(path, os.sep)
    if len(elements) > 3: path_head = '...' + os.sep
    else:                 path_head = os.sep
    return (path_head + os.sep.join(elements[-2:]))[-40:]


#------------ User's Guide support ---------- #

# The user's guide is loaded only on demand when the user requests
# display of the help window.  After loading, it will be saved for
# subsequent viewing.

from diag_globals import image_directory
from Tkinter import PhotoImage

def show_users_guide(master):
    if not helpDict: load_help()
    last_index = len(helpTopics) - 1

    def show_help(fr):
        left_fr = Frame(fr)
        Label(left_fr, text='Help Topics', font=heading2_font).pack(pady=3)
        topics = Listbox(left_fr, selectmode=SINGLE, font=text_font,
                         exportselection=0, background=text_bg_color,
                         height=20, width=24, highlightthickness=0)
        topics.pack(expand=YES, fill=Y)

        left_fr.pack(side=LEFT, padx=3, pady=0, expand=YES, fill=Y)
        for item in helpTopics:
            # add leading blank to create margin:
            topics.insert(END, ' ' + item)
        topics.selection_set(0)

        if on_win:   htext_size = 72, 26
        elif on_osx: htext_size = 68, 30
        else:        htext_size = 72, 26
        txt_fr, txt = scrolled_text_widget(
                          fr, width=htext_size[0], height=htext_size[1],
                          font=text_font, enter_focus=0,
                          tab_stops=('.5c','1c','10c'))
        txt_fr.pack(side=LEFT, padx=3, pady=0, expand=YES, fill=BOTH)

        def special_keys(event):
            if event.keysym in ('Up','KP_Up', 'Down','KP_Down'):
                sel = topics.curselection()
                if not sel: return
                topics.selection_clear(0, END)
                if event.keysym in ('Up','KP_Up'):
                    index = max(0, int(sel[0]) - 1)
                else:
                    index = min(last_index, int(sel[0]) + 1)
                topics.selection_set(index)
                help_func_index(topics, index, txt)

        wrapped_bind(fr, '<Key>', special_keys, 'Help keys')
        if not on_win:
            wrapped_bind(fr, '<Enter>', lambda event: txt.focus_set())
        select_fn = lambda event: help_func(event.widget, event.y, txt)
        wrapped_bind(topics, '<Button-1>', select_fn, 'Display help topic')
        help_func(topics, 0, txt)     # display intro

    def close_help(fr):
        app_geometry['help'] = fr.geometry()

    fr, widgets = positioned_dialog(master, [0], top_pady=0,
                      dialog_proc=show_help, final_action=close_help,
                      geometry=app_geometry['help'],
                      title="User's Guide for Diagnil")

def help_func(topics, y, txt):
    help_func_index(topics, topics.nearest(y), txt)

def help_func_index(topics, index, txt):
    top, bottom = topics.yview()
    span = bottom - top
    midpt = (top + bottom) / 2
    frac = float(index) / topics.size()
    if abs(frac - midpt) > 0.4 * span:
        topics.after(50, lambda : topics.yview_moveto(frac - 0.5 * span))

    name = topics.get(index)[1:]         # strip leading blank
    txt['state'] = NORMAL
    txt.delete(1.0, END)
    item_seq = helpDict[name]
    txt.insert(END, '%s\n\n' % name)
    txt.tag_add('topic', '1.0', '2.0')
    txt.tag_configure('topic', foreground='dark blue', justify=CENTER,
                      font=heading2_font)
    help_insert_items(item_seq, txt)
    set_scrollbars_top(txt)
    txt['state'] = DISABLED

# Insert a sequence of strings and captioned images into a Text widget.
# The image specification is a tuple of strings, one of which is assumed
# to be the image file name while the others are captions/descriptions.

def help_insert_items(item_seq, txt):
    # putting images on a list saves references to prevent GC of image objects
    txt.image_cache = []
    for item in item_seq:
        if isinstance(item, basestring):
            insert_annotated_text(txt, item)
        else:   # tuple of image file names with caption at beginning/end
            for string in item:
                if string.endswith('.gif'):
                    image_obj = PhotoImage(file=os.path.join(image_directory,
                                                             string))
                    txt.image_cache.append(image_obj)
                    txt.image_create(END, image=image_obj)
                else:
                    txt.insert(END, string)
            txt.insert(END, '\n\n')

def load_help():
    global helpDict, helpTopics
    import diag_help
    if on_osx: accel = 'Command+'
    else:      accel = 'Ctrl+'
    def adjust_text(text):    # customize by platform
        if isinstance(text, basestring):
            return text.replace('Ctrl-Cmd-', accel)
        else:
            return text    # image
    helpDict = {}
    for topic_item in diag_help.helpItems:
        topic, text_seq = topic_item[0], topic_item[1:]
        helpDict[topic] = map(adjust_text, text_seq)
    if on_osx:
        helpDict['Application Menu'] += diag_help.osx_comment
    # following preserves heading order; using dict functions does not
    helpTopics = [ item[0] for item in diag_help.helpItems ]
