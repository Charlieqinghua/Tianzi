
# Dialog, warning and error messages.

display_messages = \
    {'internal_error' :
     "Unfortunately, an internal error has been detected, " 
     "which means the software probably contains a latent bug. "
     "If you would be kind enough to report the problem by e-mail, " 
     "the author can make corrections in the next version. " 
     "After closing this alert box, press F1 to view the " 
     "reporting procedure. In any case, it would be wise to " 
     "save your unfinished puzzle in a new file (use Save As), "
     "then restart Diagnil before proceeding. You should "
     "Undo first if words were lost. "
     "Sorry for any inconvenience." ,

     'reporting_procedure' :
     "If you are viewing this after experiencing a software problem, " 
     "a log file containing error information has just been written. " 
     "To report the problem you encountered, simply "
     "send an e-mail message to the author at the address shown " 
     "below, making sure to include the file cited below as an attachment. " 
     "You might want to check this web page first "
     "to see if the bug has been fixed:\n\n"
     "http://blueherons.org/diagnil/diag-news.html\n\n"
     "You may use the buttons to copy the address and file name to " 
     "your computer's clipboard for pasting in your e-mail program. " 
     "Please include a brief description in your message of what you " 
     "were trying to do when the error occurred and whether you noticed " 
     "any anomalies up to that point." ,

     'privacy_notice' :
     "Privacy notice: The file above contains information about " 
     "the software's internal state, including words from the " 
     "current puzzle. No other data has been incorporated.\n\n"
     "Thank you very much for taking the time to report this problem." ,
     }


dialog_messages = \
    {'confirm_close' :
     ('Close puzzle',
      "The latest changes to the current puzzle have not yet been saved. "
      "Do you want to continue the "
      "requested action anyway (discarding latest changes)?") ,

     'delete_dg0_files' :
     ('Exit Diagnil',
      "You have been running Diagnil in trial mode without having "
      "installed the application. If you will not be using it again, "
      "it would be best to delete its user data and preference files. "
      "Would you like to delete Diagnil's user files?" ),
     
     'puz_file_not_diagramless' :
     ('Open puzzle file',
      "It appears that this file was not prepared as a "
      "diagramless puzzle. You might prefer "
      "to use Across Lite or a similar software client to "
      "work with this file. Would you like to proceed anyway "
      "and open it for diagramless solving?") ,
     
     'jpz_file_not_diagramless' :
     ('Open puzzle file',
      "It's unclear whether this file was prepared as a "
      "diagramless puzzle. Would you like to proceed anyway "
      "and open it for diagramless solving?") ,

     'confirm_missing_finalize' :
     ('Finalize puzzle',
      "The apparent words whose first letters are shown in red "
      "boxes have not been declared. Select Cancel to go back and add "
      "the missing words. Note, however, that some nonstandard "
      "puzzle designs use uncrossed squares "
      "(not every letter occurs in a crossing word). "
      "Would you like to finalize this puzzle now "
      "(ignoring the missing words)?") ,

     'confirm_complete_words' :
     ('Finalize puzzle',
      "The apparent words whose first letters are shown in red "
      "boxes have not been entered. "
      "Would you like to complete the puzzle by automatically entering "
      "these additional words?") ,

     'confirm_unchecked' :
     ('Finalize puzzle',
      "A puzzle solution is available but it is currently locked. "
      "If you have the key, you can select Cancel to go back and unlock "
      "the solution, then try to finalize the puzzle again. "
      "Otherwise, you can continue and the puzzle will be finalized "
      "without being checked against the solution.") ,

     'confirm_delete' :
     ('Delete puzzle files',
      "You have selected the following puzzle files for deletion: %s. "
      "Please confirm that you would like to carry out the deletion "
      "of these files from the folder '%s'.") ,   ## (file_list, folder)

     'confirm_revelation' :
     ('Reveal solution',
      "You have asked to reveal the entire puzzle solution. "
      "Please confirm that you would like to proceed. ") ,

     'try_another_destination' :
     ('Move words',
      "Would you like to try another destination for moving these words?") ,
    }


error_messages = \
    {'invalid_open' :
     ('Open puzzle file',
      "Either file '%s' does not exist or an error occurred "
      "while reading it.") ,  ## % puz_file

     'old_file_version' :
     ('Open puzzle file',
      "This puzzle file was created by an older version (%s) of Diagnil. "
      "Unfortunately, this file is incompatible with the current "
      "version and cannot be opened.") ,  ## version

     'corrupted_open' :
     ('Open puzzle file',
      "Either '%s' is not a puzzle file or it has been corrupted somehow.") ,
      ## % puz_file

     'unsupported_open' :
     ('Open puzzle file',
      "The puzzle file '%s' is using features that currently are "
      "not supported by Diagnil.") ,
      ## % puz_file
     
     'corrupted_open_clues' :
     ('Open clue file',
      "Either '%s' is not a diagramless clue file or it has been "
      "corrupted somehow.") ,
      ## % clue_file
     
     'open_unknown_variant' :
     ('Open puzzle file',
      "File '%s' could not be opened successfully. It might be an "
      "ill-formed puzzle file or possibly an unsupported variant.") ,
      ## % puz_file
     
     'not_a_crossword' :
     ('Open puzzle file',
      "The file '%s' is not recognizable as a crossword puzzle, "
      "diagramless or otherwise. It could be a puzzle of some other kind.") ,
      ## % puz_file
     
     'invalid_save' :
     ('Save puzzle file',
      "The puzzle's file or path name is invalid, or you lack the "
      "required permission to write this file.") ,

     'no_nonpuz_deletion' :
     ('Delete puzzle files',
      "A subset of your selected files do not appear to be "
      "puzzle files: %s. For safety's sake, only puzzle files "
      "from the folder '%s' are accepted for deletion. Please use "
      "the regular services of your operating system to delete "
      "other file types.") ,  ## (file_list, folder)
     
     'no_undo' :
     ('Undo', "There are no more undoable steps.") ,
     
     'no_redo' :
     ('Redo', "There are no more redoable (recently undone) steps.") ,
     
     'already_final' :
     ('Start action',
      "The puzzle has been finalized.  Select Undo or type Control-Z "
      "to enable changes again.") ,

     'no_puz_defn' :
     ('Unlock solution',
      "There is no currently open puzzle definition that has a solution.") ,

     'no_clues_available' :
     ('View clues',
      "There are no clues available to display.") ,

     'no_clipboard_clues' :
     ('Import clues',
      "There are no clues -- the clipboard is empty.") ,

     'invalid_clues' :
     ('Import clues',
      "There are errors in the clue list -- one or more "
      "sections seem to be missing.") ,

     'invalid_clue_specific' :
     ('Import clues',
      "There is an error in the %s clue list "
      "at these lines:\n\n%s") ,  ## (dir_text, bad_lines)

     'bad_clue_form' :
     ('Edit imported clues',
      "This is not a well-formed clue. It should contain a "
      "valid clue number followed by a phrase.") ,

     'bad_clue_number' :
     ('Edit imported clues',
      "There is no clue numbered %d to delete.") ,  ## num

     'select_displayable' :
     ('Display clues',
      "No selection has been made. Please select a clue that you "
      "would like to have displayed.") ,

     'select_revealable' :
     ('Check/reveal solution',
      "No selection has been made. Please select a word/clue that you "
      "would like to have checked/revealed.") ,

     'both_revealable' :
     ('Check/reveal solution',
      "Both Across and Down words/clues have been selected. "
      "Deselect the one you don't want checked/revealed "
      "(click on the Clear button).") ,

     'selection_unentered' :
     ('Check/reveal solution',
      "The selected word has not been entered on a word list "
      "and therefore its letters cannot be checked.") ,

     'selection_ungridded' :
     ('Check/reveal solution',
      "The selected word has not been placed on the main grid "
      "and therefore its position cannot be checked.") ,

     'solution_locked' :
     ('Check/reveal solution',
      "The puzzle solution is currently locked. Select the Unlock "
      "menu item to make the solution available.") ,
     
     'bad_key_digits' :
     ('Unlock solution',
      "The key string '%s' is not well-formed. A valid key consists "
      "of four decimal digits.") ,  ## % key
     
     'bad_solution_key' :
     ('Unlock solution',
      "The key %s did not correctly unlock the puzzle solution. "
      "Please check the key digits and try again.") ,  ## % key
     
     'unscrambling_error' :
     ('Unlock solution',
      "A data error occurred while unlocking the puzzle solution. "
      "If the problem persists, the puzzle file might be corrupted.") ,
     
     'cannot_recall_arb' :
     ('Recall previous word',
      "No word is available to be recalled.") ,
     
     'invalid_pattern' :
     ('Word search',
      "The search pattern is invalid. Only letters and "
      "the characters '.', '*' and '?' are allowed.") ,

     'empty_deletion' :
     ('Delete word entry',
      "No word number was provided. "
      "Select an entry from the word list or type a word number.") ,

     'nonexistent_deletion' :
     ('Delete word entry',
      "No word having number %s currently exists. ") ,   ## % num

     'final_while_mini' :
     ('Finalize puzzle',
      "The puzzle cannot be finalized while minigrids are nonempty.") ,

     'diagonal_id_mismatch' :
     ('Move region using diagonal',
      "The diagonal endpoints must lie on the same grid.") ,

     'no_multiword_redo' :
     ('Move words again',
      "There is no word selection from a preceding movement command "
      "that can be reused.") ,

     'bad_word_extension' :
     ('Place word',
      "A word extension based on '%s' could not be created. Place the "
      "mouse/key cursor over a cell to perform this action.") ,  ## % word

     'no_word_number' :
     ('Place word',
      "A word number was not supplied and none "
      "could be inferred from the grid.") ,

     'extra_word_number' :
     ('Enter word',
      "Word number %s does not appear in the list of %s clues.") ,
     ## % (num, dir_text[dir])

     'no_word_letters' :
     ('Place word',
      "Word %s was not found in the list of %s words, nor could "
      "a word be inferred from the grid.") ,     ## % (num, dir_text[dir])

     'cannot_infer_number' :
     ('Paste word',
      "A word number cannot be inferred from the grid, "
      "which means this is an invalid place for a word. If you really "
      "want to place a word at this cell, you need to rearrange first.") ,

     'out_of_bounds' :
     ('Place word on grid',
      "Word '%s' extends past the grid boundaries.") ,   ## % word
     
     'place_conflict' :
     ('Place word on grid',
      "Word '%d %s' and its end blocks conflict with other "
      "word/block placement(s).") ,     ## % (num, word)
     
     'extend_crossing' :
     ('Place word on grid',
      "New %s word '%s' will conflict with the end blocks of "
      "%s word(s) %s. Would you like to extend the crossing word(s) "
      "with letters from the new word?") ,
     ## % (dir_text[dir], word, dir_text[1-dir], ext_nums)

     'head_cell_split' :
     ('Place word on grid',
      "Word %d %s is not being placed in the same cell as existing "
      "word %d %s.") ,   ## % (num, dir_text[dir], num, dir_text[1-dir]))

     'head_cell_clash' :
     ('Place word on grid',
      "Word %d %s is being placed in the same cell as existing "
      "word %d %s.") ,   ## % (num, dir_text[dir], cell[0], dir_text[1-dir])

     'invalid_word_entry' :
     ('Parse word entry',
      "The word entry '%s' is invalid. A number followed by a word is the "
      "basic form. See the User's Guide for special cases.") ,  ## % txt

     'zero_word_number' :
     ('Parse word entry', "Zero is not a valid word number.") ,

     'renumber_info_missing' :
     ('Renumber word',
      "To renumber, both a word and a new number must exist at the "
      "chosen cell, or the new number must be typed in the word entry "
      "box while the mouse/key cursor lies on the cell.") ,

     'renumber_off_grid' :
     ('Renumber word',
      "To renumber a word, the cursor must be placed at the word "
      "on its grid.") ,

     'rotate_word_missing' :
     ('Rotate word',
      "Word %d-%s does not exist.") ,    ## % (num, dir_text[dir])

     'bad_puzzle_size' :
     ('Declare puzzle size',
      "There is a problem with the value of width/height '%s'. "
      "It should be a number in the range of 3 to %s.") ,
      ## % (width/height, max_size)

     'size_not_square' :
     ('Declare puzzle size',
      "Diagonal symmetry requires that the puzzle be square "
      "(width = height).") ,

     'bad_user_directory' :
     ('Diagnil start-up',
      "It was not possible to locate or create "
      "the expected user folder "
      "while starting up the application. It could be that Diagnil is "
      "incompatible with your computer or operating system platform. "
      "You may proceed, but beware that you might not be able to save "
      "any puzzle files. If the problem persists, "
      "consider contacting the author for more information.") ,

     'bad_preferences' :
     ('Diagnil preferences',
      "While reading the preference settings file, an error was detected " 
      "indicating that the file is missing or corrupted. "
      "A new file will be created with default settings. "
      "Select 'Preferences' from the Edit menu to adjust these settings. ") ,

     'settings_not_current' :
     ('Diagnil preferences',
      "It appears that the preference settings file was modified " 
      "by another instance of Diagnil after this session began. "
      "To avoid inconsistencies, the changes you are requesting "
      "will not be saved. To make these changes, close all instances "
      "of Diagnil, then restart it and edit your preferences again.") ,
     }


info_messages = \
    {'already_unlocked' :
     ('Unlock solution',
      "The puzzle solution was already unlocked or "
      "had never been locked.") ,

     'prefs_changed' :
     ('Change preferences',
      "The new preference settings have been saved. "
      "They will take effect the next time Diagnil is started.") ,
     }


warning_messages = \
    {'out-of-order' :
     ('Place word on grid',
      "The new word placement(s) will leave one or more words on the "
      "grid out of order. Undo if this is unintentional. "
      "Proceed if this is only temporary while rearranging the grid. "
      "You should restore order as soon as possible.") ,

     'extension_num_override' :
     ('Extending word on grid',
      "The word number(s) explicitly supplied or inferred from "
      "the grid are being overridden. Instead, the number of the "
      "existing word being extended is preferred.") ,

     'word_too_short' :
     ('Enter word',
      "New word '%s' has less than three letters, suggesting "
      "it is probably missing one or more letters.") ,
     ## % word

     'duplicate_word' :
     ('Enter word',
      "New word '%s' was previously entered as word %d-%s. One of these, "
      "either the new or old version, is probably an erroneous duplicate.") ,
     ## % (word, old_num, dir_text[old_dir])
     
     'unconfirmed_overwrite' :
     ('Enter word',
      "Preexisting word '%s' had been assigned to %d-%s. "
      "It was overwritten by new word '%s'. Undo to restore '%s'.") ,
     ## % (old_word, num, dir_text, word, old_word)

     'size_cant_change' :
     ('Set size and symmetry',
      "This puzzle's size is already known so its grid boundaries "
      "are fixed and may not be changed.") ,

     'size_symm_session' :
     ('Set size and symmetry',
      "The session's new size and symmetry defaults will be applied "
      "when the next puzzle is opened.") ,
     
     'multiple_XPF_open' :
     ('Open puzzle file',
      "This XPF-formatted file contains multiple puzzles. Only the first "
      "one will be opened.") ,

     'using_dg0_ext' :
     ('Save puzzle file',
      "The puzzle and your current solution are being saved in "
      "the Diagnil file format (file name %s). "
      "Open this file to resume your work. The original puzzle "
      "file (%s) is no longer needed.") ,
     ## % (diag_file, puz_file)
    }

