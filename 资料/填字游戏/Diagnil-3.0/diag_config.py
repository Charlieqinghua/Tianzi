#  Diagnil: Diagramless Crossword Assistant
#      A utility for solving diagramless puzzles interactively
#
#  Copyright (c) 2003-2012, Ben Di Vito.
#
#  This is open source software, distributed under a BSD-style license.
#  See the accompanying file 'License' for details.
#

# Diagnil version parameters

version           = '3.0'
release_date      = 'August 2012'
full_release_date = ' 4 August 2012'

copyright_dates   = '2003-2012'
email_addr        = 'bdivito@cox.net'
home_page         = 'blueherons.org/diagnil/'

# The latest version where the file format changed:

last_file_version_change = [1, 0]    # 1.0

# Names of preference settings not requiring adjustment on startup.

unadjusted_prefs = (
    ('infer_nums', 1),
    ('key_navigation', 1),
    ('auto_complete', 1),
    ('upper_case', 0),
    ('wide_layout', 0),
    ('apply_symmetry', 1),
    ('symmetry_type', 'rot'),
    ('show_boundary', 1),
    ('puzzle_width', 17),
    ('puzzle_height', 17),
    ('max_undo', 10),
    )

recent_settings = (
    ('open_files', []),
    ('latest_puzzle_dir', ''),
    ('latest_clues_dir', ''),
    )

# Debug flags (must be set before session begins):

check_assertions  = 0
collect_time_data = 0

exclude_time_data = ['motion_action', 'move_preview']

