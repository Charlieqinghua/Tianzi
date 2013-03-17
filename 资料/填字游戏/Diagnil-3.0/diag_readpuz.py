# This module provides for reading crossword files encoded in several
# different formats.

# Some of this module is based on the .puz file documentation compiled
# by several observers.  See the Acknowledgements section of the
# README file for details.

# In general, the checksums are ignored while reading a .puz file.
# They seem to be anachronistic.  Maybe they helped 20 years ago, but
# their benefit is doubtful with today's data communications.

# The diagramless variant is recognized while other cases are not
# distinguished by puzzle type.  Certain files (e.g., for cryptic
# puzzles) are not identified and so would be mishandled.


# This class is used to open a .puz file (Across Lite binary format)
# and extract its contents.  It also works for .jpz (Crossword Solver),
# .xpf and .ipuz files.  The attributes saved are:
#
#     format_type: string                    puz, jpz, xpf, ipuz, scanned
#     width, height: int
#     nums:  dir -> [num,...]                across, down word numbers
#     clues: dir -> [clue,...]               across, down clue lists
#     soln_grid:  [letter-row,...]           solution letters
#     soln_cksum: int                        solution checksum
#     soln_flags: int                        nonzero if solution locked
#     soln_words: dir -> {num -> word}       solution words
#     soln_posns: dir -> {num -> (row, col)} solution positions
#     title, author, copyright: string
#     notes: string                          optional
#     symmetry_type: string


# Added in version 2.2: a new clueful mode for the XPF crossword format.
# The XPF Puzzle specification was created by Jim Horne.  It is licensed
# under a Creative Commons Attribution-No Derivative Works 3.0
# Unported License. 
#
# This new mode is preliminary and experimental for use with XPF files,
# which are XML documents.  If use of this format becomes widespread,
# XPF features might be expanded.  Right now only the basics are handled.
# This should suffice do everything currently done with Across Lite
# except for locked puzzles.

# Also added in 2.2: a semi-clueful mode where clues have been obtained
# by scanning from a printed source and then processed with OCR software.
# A partial PuzzleDefn object is created after the clues have been 
# retrieved and edited by the user.  No puzzle file importing is involved
# in this case, but the data structure is used for consistency.

# Added in version 2.4: a new clueful mode for the ipuz puzzle format.
# The ipuz puzzle specification was created by Roy Leban of Puzzazz, Inc.
# It is licensed under a Creative Commons Attribution-No Derivative Works
# 3.0 Unported License. 

# Added in version 3.0: a new clueful mode for the jpz puzzle format.
# The jpz puzzle format was created by Antony Lewis of WordWeb Software.
# Per the author, this format is considered open.


import os, string
from diag_globals   import *
from diag_util      import *

_jsonp = re.compile('\s*ipuz\((.*)\)\s*')    # JSONP format: ipuz(<obj>)


class PuzzleDefn:
    def __init__(self, filename, warnings, puz_content='',
                 use_anyway=0, file_ext='puz', semi_clueful=0):
        if file_ext in default_ipuz_ext:
            self.parse_ipuz(filename, warnings, puz_content, use_anyway)
        elif file_ext in default_xpf_ext:
            self.parse_xpf(filename, warnings, puz_content, use_anyway)
        elif file_ext in default_jpz_ext:
            self.parse_jpz(filename, warnings, puz_content, use_anyway)
        elif semi_clueful:
            self.retrieve_clues(filename, puz_content)
        else:
            self.parse_puz(filename, puz_content, use_anyway)


#-------------- puz file processing --------------

    # Handle default, assumed to be in Across Lite format.

    def parse_puz(self, filename, puz_content, use_anyway):
        if puz_content:
            puz = puz_content
        else:
            puz = file(filename, 'rb').read()
        if puz[0x02 : 0x0e] != 'ACROSS&DOWN\0':
            raise IOError

        self.format_type = 'puz'
        wid = self.width  = ord(puz[0x2c])
        ht =  self.height = ord(puz[0x2d])
        grid_len = wid * ht
        pos = 0x34            # start of solution grid

        if puz.find('.', pos, pos + grid_len) >= 0:
            # black square char != ':' => not diagramless
            if use_anyway:
                self.black = '.'
            else:
                raise ValueError  
        else:
            self.black = ':'              # diagramless case

        import struct
        self.soln_cksum = struct.unpack('H', puz[0x1e:0x20])[0]
        self.soln_flags = struct.unpack('H', puz[0x32:0x34])[0]

        self.soln_grid = []
        for row in range(ht):
            self.soln_grid.append(puz[pos:pos+wid])
            pos += wid
        # pos now points to user guess grid
        self.index = pos + grid_len  # skip over guess grid
        # index points to start of text area

        def clean(s):
            # purge unprintable characters
            return ''.join([ c for c in s if c in string.printable ])

        def read_string():
            end = puz.find(chr(0), self.index)
            s = ''.join(map(unichr, map(ord, puz[self.index:end])))
            s = s.strip().replace('\r\n', '\n')
            self.index = end + 1
            return s

        self.title     = clean(read_string())
        self.author    = clean(read_string())
        self.copyright = clean(read_string())

        clues = []
        clue = read_string()
        while clue:
            clues.append(clue)
            clue = read_string()
        num_clues = self.parse_clues_soln(clues)

        if len(clues) > num_clues:
            self.notes =  clean(clues[num_clues])  ### notes optional
        else:
            self.notes = 'There are no notes.'
        self.symmetry_type = infer_symmetry_type(self.notes)

# Derive word numbers, clue lists and solution lists from grid structure.
# If clue list is provided, match clues with word numbers and set class
# attributes for clues and nums.  If nums_only is indicated, skip the
# clues attribute.

    def parse_clues_soln(self, clues=None, nums_only=0):
        # Clue numbers need to be derived based on puzzle shape.
        wid, ht = self.width, self.height
        black = self.black

        # form grid as row strings; prepend, append rows of blacks
        black_row = black * wid
        grid = [black_row] + self.soln_grid + [black_row]
        n = 0
        nums = []
        asoln, dsoln = {}, {}

        # Scan rows, collecting word numbers as new ones are found.
        # Across word numbers are positive; down word numbers are negative.
        # When both an across word and a down word start in the same cell,
        # there will be both a +n and a -n appended.
        # Also collect across words for solution dictionaries.

        for r in range(1, ht+1):
            not_in_word = 1
            for c in range(wid):
                cell = grid[r][c]
                if cell == black:
                    not_in_word = 1
                elif not_in_word:       # start of new across word
                    not_in_word = 0
                    n += 1
                    nums.append(n)
                    aword = [cell]
                    asoln[n] = ((r-1, c), aword)
                    if grid[r-1][c] == black:    # start of new down word
                        nums.append(-n)
                        dsoln[n] = (r-1, c)
                elif grid[r-1][c] == black:      # start of new down word
                    n += 1
                    nums.append(-n)
                    aword.append(cell)
                    dsoln[n] = (r-1, c)
                else:
                    aword.append(cell)
        asoln_words, asoln_posns = {}, {}
        for num, posn_word in asoln.items():
            posn, word = posn_word
            asoln_words[num] = ''.join(word)
            asoln_posns[num] = posn

        # Find down words given positions derived above.

        dsoln_words, dsoln_posns = {}, {}
        for num, posn in dsoln.items():
            r, c = posn
            r += 1                         # account for first black row
            word = []
            while grid[r][c] != black:     # trailing black row ensures a halt
                word.append(grid[r][c])
                r += 1
            dsoln_words[num] = ''.join(word)
            dsoln_posns[num] = posn
        self.soln_words = (asoln_words, dsoln_words)
        self.soln_posns = (asoln_posns, dsoln_posns)

        if clues:
            num_clues = zip(nums, clues)
            self.nums  = ([  c[0] for c in num_clues if c[0] > 0 ],
                          [ -c[0] for c in num_clues if c[0] < 0 ])
            self.clues = ([ c[1] for c in num_clues if c[0] > 0 ],
                          [ c[1] for c in num_clues if c[0] < 0 ])
            return len(nums)
        elif nums_only:
            self.nums  = ([  n for n in nums if n > 0 ],
                          [ -n for n in nums if n < 0 ])
            return len(nums)
        else:
            return 0          # requested solution only

    # Scrambling requires input in column-major order without black squares.

    def transpose_scramble_input(self):
        result = []
        for k in range(self.width):
            column = [ row[k] for row in self.soln_grid ]
            result.extend([ c for c in column if c.isalpha() ])
        return ''.join(result)

    def transpose_scramble_output(self, scr):
        result = [ [] for row in self.soln_grid ]
        i = 0
        for c in range(self.width):
            orig_column = [ row[c] for row in self.soln_grid ]
            for r in range(self.height):
                if orig_column[r].isalpha():
                    result[r].append(scr[i])
                    i += 1
                else:
                    result[r].append(orig_column[r])
        return [ ''.join(row) for row in result ]

    # Unlocking requires the correct 4-digit key.  When given a key, the
    # checksum for the unscrambled text is generated.  If it fails to
    # match the checksum stored in the .puz file, the key must be wrong.

    def unlock_solution(self, key):
        try:
            scr = self.transpose_scramble_input()
            unscr = unscramble(scr, key)
            cksum = cksum_region(unscr, 0x0000)
            if cksum != self.soln_cksum:
                raise KeyError
            new_soln = self.transpose_scramble_output(unscr)
            if map(len, new_soln) != map(len, self.soln_grid):
                raise ValueError
            self.soln_grid = new_soln
            self.soln_flags = 0
        except KeyError:
            raise KeyError
        except:
            # in case unscrambling has anomalies
            raise ValueError
        self.parse_clues_soln()    # recompute solution words and positions


#-------------- XPF file processing --------------

# Parse a file in XPF format (an XML document) and construct a
# PuzzleDefn object using the same data structures as for AL format.
# The Python xml.etree library (ElementTree) is used for parsing.
# This means Python 2.5 or later is needed.

    def parse_xpf(self, filename, warnings, puz_content, use_anyway):
        import xml.etree.ElementTree as ET

        if puz_content:
            tree = ET.fromstring(puz_content)
        else:
            tree = ET.parse(filename)
        puz_root = tree.getroot()
        puzzles = puz_root.findall('Puzzle')
        if puz_root.tag != 'Puzzles' or not puzzles:
            raise IOError
        if len(puzzles) > 1:
            warnings['multiple_XPF_open'] = 1
        puz = puzzles[0]     # currently handles only one puzzle

        def read_string(elem, tag):
            s = elem.find(tag)
            return s != None and s.text or ''

        self.format_type = 'xpf'
        self.puzzle_type  = read_string(puz, 'Type')
        if self.puzzle_type.lower() != 'diagramless' and not use_anyway:
            raise ValueError

        size = puz.find('Size')
        wid = self.width  = int(read_string(size, 'Rows') or '0')
        ht =  self.height = int(read_string(size, 'Cols') or '0')
        self.soln_cksum = 0
        self.soln_flags = 0

        self.title  = read_string(puz, 'Title')
        self.author = read_string(puz, 'Author')
        self.editor = read_string(puz, 'Editor')
        self.publisher = read_string(puz, 'Publisher')
        self.date   = read_string(puz, 'Date')
        self.copyright = read_string(puz, 'Copyright')
        if not self.copyright:
            if self.publisher and self.date:
                self.copyright = \
                    self.date.split('/')[-1] + ', ' + self.publisher
            else:
                self.copyright = self.date.split('/')[-1] + self.publisher
        self.notes = read_string(puz, 'Notepad') or 'There are no notes.'
        self.symmetry_type = infer_symmetry_type(self.notes)

        self.soln_grid = [ r.text for r in puz.find('Grid').findall('Row') ]
        clues = puz.find('Clues').findall('Clue')
        if 'Row' not in clues[0].keys():
            # Missing clue attributes. Assume puz-style clue encoding, i.e.,
            # clues ordered with across-down interleaving.
            self.black = '.'
            self.parse_clues_soln([ c.text for c in clues ])
            return

        aclues = [ c for c in clues if c.get('Dir', 'Across') == 'Across' ]
        dclues = [ c for c in clues if c.get('Dir', 'Across') == 'Down' ]

        # currently assumes all clue attributes are present
        self.nums  = [ [ int(c.get('Num', '999')) for c in clist ]
                       for clist in (aclues, dclues) ]
        self.clues = [ [ c.text for c in clist ]
                       for clist in (aclues, dclues) ]
        self.soln_words = [ dict([ (n, c.get('Ans', '???'))
                                   for n,c in zip(nums, clist) ])
                            for nums, clist
                            in zip(self.nums, (aclues, dclues)) ]
        self.soln_posns = [ dict([ (n, (int(c.get('Row', '999')) - 1,
                                        int(c.get('Col', '999')) - 1))
                                   for n,c in zip(nums, clist) ])
                            for nums, clist
                            in zip(self.nums, (aclues, dclues)) ]


#-------------- jpz file processing --------------

# Parse a file in jpz format (Crossword Compiler), which is a
# zip-compressed XML document.  Construct a PuzzleDefn object using
# the same data structures as for puz format.
# The Python xml.etree library (ElementTree) is used for parsing.
# This means Python 2.5 or later is needed.

    def parse_jpz(self, filename, warnings, puz_content, use_anyway):
        import xml.etree.ElementTree as ET

        def read_string(elem, tag):
            s = elem.find(prefix + tag)    # add namespace prefix
            return s != None and s.text or ''

        if puz_content:
            tree = ET.fromstring(puz_content)
        else:
            import zipfile
            zipf = zipfile.ZipFile(filename)
            members = zipf.namelist()
            tree = ET.parse(zipf.open(members[0]))
            zipf.close()
        puz_root = tree.getroot()

        # ElementTree adds the namespace URI as a prefix to element tags,
        # making them appear as {URI}tag
        for elem in puz_root.findall('*'):
            prefix, elem_name = elem.tag.split('}')
            if elem_name == 'rectangular-puzzle': break
        puzzle = puz_root and elem
        if not puzzle:
            raise IOError           # could be wrong puzzle type
        if prefix: prefix += '}'
        metadata = puzzle.find(prefix + 'metadata')
        puz = puzzle.find(prefix + 'crossword')

        if puz == None:
            raise NotACrossword
        self.notes = read_string(metadata, 'description') or \
                     'There are no notes.'        
        self.title  = read_string(metadata, 'title')
        if 'diagramless' in (self.notes + self.title).lower() :
            self.puzzle_type = 'Diagramless'
        elif use_anyway:
            self.puzzle_type = 'Regular'
        else:
            raise ValueError

        self.format_type = 'jpz'
        grid = puz.find(prefix + 'grid')
        wid = self.width  = int(grid.get('width', '0'))
        ht =  self.height = int(grid.get('height', '0'))
        self.soln_cksum = 0
        self.soln_flags = 0

        self.author = read_string(metadata, 'creator')
        self.editor = read_string(metadata, 'editor')
        self.publisher = read_string(metadata, 'publisher')
        self.date   = read_string(metadata, 'created')
        self.copyright = read_string(metadata, 'copyright')
        if not self.copyright:
            if self.publisher and self.date:
                self.copyright = \
                    self.date.split('/')[-1] + ', ' + self.publisher
            else:
                self.copyright = self.date.split('/')[-1] + self.publisher
        self.symmetry_type = infer_symmetry_type(self.notes)

        # 'clue' elements contain word numbers and clue text
        self.nums, self.clues = [None, None], [None, None]
        for clue_list in puz.findall(prefix + 'clues'):
            clue_dir = clue_list.find(prefix + 'title')
            dir = int('Down' in clue_dir.find(prefix + 'b').text)
            clues = clue_list.findall(prefix + 'clue')
            self.nums[dir]  = [ int(c.get('number')) for c in clues ]
            self.clues[dir] = [ map_html(c.text) for c in clues ]

        # 'cell' elements contain solution letters or blocks;
        # word numbers appear for head cells
        soln_grid = [ [None] * wid for row in range(ht) ]
        self.black = '.'
        for cell in grid.findall(prefix + 'cell'):
            r, c = int(cell.get('y')) - 1, int(cell.get('x')) - 1
            if cell.get('type') == 'block':
                soln_grid[r][c] = self.black, 0
            else:
                soln_grid[r][c] = \
                    cell.get('solution'), int(cell.get('number', '0'))
            # collecting tuples (soln_letter, word_number)

        self.soln_words = [{}, {}]
        self.soln_posns = [{}, {}]
        # 'word' elements give position and range of words;
        # row or col value is of form 'm-n' (1-based)
        for word in puz.findall(prefix + 'word'):
            rows, cols = word.get('y'), word.get('x')
            dir = int('-' in rows)    # 1 for down
            if dir:
                col = int(cols) - 1
                rows = map(int, rows.split('-'))
                posn = rows[0] - 1, col
                letters = [ soln_grid[r][col][0]
                            for r in range(posn[0], rows[1]) ]
            else:
                row = int(rows) - 1
                cols = map(int, cols.split('-'))
                posn = row, cols[0] - 1
                letters = [ soln_grid[row][c][0]
                            for c in range(posn[1], cols[1]) ]
            word_num = soln_grid[posn[0]][posn[1]][1]
            self.soln_words[dir][word_num] = ''.join(letters)
            self.soln_posns[dir][word_num] = posn

        # collect letters into rows to form solution grid a la puz files
        self.soln_grid = [ ''.join([ soln_grid[r][c][0] for c in range(wid) ])
                           for r in range(ht) ]

 
#-------------- ipuz file processing --------------

# Parse a file in ipuz format (a JSON data string) and construct a
# PuzzleDefn object using the same data structures as for AL format.
# The Python JSON library is used for parsing.
# This means Python 2.6 or later is needed.

    def parse_ipuz(self, filename, warnings, puz_content, use_anyway):
        try:
            import json
        except ImportError:
            import simplejson as json    # for Python 2.5 case on Win XP

        if not puz_content:
            puz_content = [ s.strip() for s in
                            file(filename).readlines() ]    ### IO excep
            puz_content = ' '.join(puz_content)
        match = _jsonp.match(puz_content)
        # Accept either JSON or JSONP format.
        # JSONP format: ipuz(<JSON object>)
        if match:
            puz_content = match.group(1)
        puz = json.loads(puz_content)

        if not (isinstance(puz, dict) and
                puz['version'].startswith('http://ipuz.org')):
            raise IOError

        def ipuz_field(puz_obj, field, default='raise_excep'):
            value = puz_obj.get(field, ())   # JSON won't return tuples
            if value == ():
                if default == 'raise_excep': raise ValueError
                else:                        return default
            return value

        self.format_type = 'ipuz'
        puz_kind = ipuz_field(puz, 'kind')[0].split('#')[0]
        if puz_kind == 'http://ipuz.org/crossword/diagramless':
            self.puzzle_type = 'Diagramless'
        elif puz_kind != 'http://ipuz.org/crossword':
            raise NotACrossword
        elif use_anyway:
            self.puzzle_type = 'Regular'
        else:
            raise ValueError

        size = ipuz_field(puz, 'dimensions')
        wid = self.width  = int(size['width'])
        ht =  self.height = int(size['height'])
        self.soln_cksum = 0
        self.soln_flags = 0

        self.title     = map_html(ipuz_field(puz, 'title', ''))
        self.author    = map_html(ipuz_field(puz, 'author', ''))
        self.editor    = map_html(ipuz_field(puz, 'editor', ''))
        self.publisher = map_html(ipuz_field(puz, 'publisher', ''))
        self.date      = ipuz_field(puz, 'date', '')
        self.copyright = ipuz_field(puz, 'copyright', '')
        if not self.copyright:
            if self.publisher and self.date:
                self.copyright = \
                    self.date.split('/')[-1] + ', ' + self.publisher
            else:
                self.copyright = self.date.split('/')[-1] + self.publisher
        self.notes =  map_html(ipuz_field(puz, 'notes', 'There are no notes.'))
        self.symmetry_type = infer_symmetry_type(self.notes)
        self.black = ipuz_field(puz, 'block', '#')  # called 'black' elsewhere
        empty = ipuz_field(puz, 'empty', 0)

        solution = ipuz_field(puz, 'solution', [])
        if solution:
            for row in solution:
                for cell in row:
                    if not isinstance(cell, basestring):
                        # accept only string-valued CrosswordValues,
                        # which are either blocks or letters
                        raise OffNominal
            self.soln_grid = [ ''.join(row) for row in solution ]
        else:
            # need to extract structure from 'puzzle' field;
            # create a dummy soln_grid using '?' for letters
            puzzle = ipuz_field(puz, 'puzzle')
            self.soln_grid = []
            for row in puzzle:
                soln_row = []
                for cell in row:
                    if cell == empty or isinstance(cell, int):
                        soln_row.append('?')
                    else:
                        soln_row.append(cell)
                self.soln_grid.append(''.join(soln_row))
            # soln_grid is now suitable for applying parse_clues_soln

        all_clues = ipuz_field(puz, 'clues', {'Across': [], 'Down': []})
        clues = ( all_clues['Across'], all_clues['Down'] )
        # assume that all clues use the same type/option
        if isinstance(clues[0][0], basestring):
            # Unnumbered clues are just strings.
            self.clues = [ [ map_html(c) for c in clist ] for clist in clues ]
        elif isinstance(clues[0][0], list) and \
                isinstance(clues[0][0][1], basestring):
            # Numbered clues are pairs: [num, "clue"]
#            self.nums  = [ [ int(c[0]) for c in clist ] for clist in clues ]
            self.clues = [ [ map_html(c[1]) for c in clist ]
                           for clist in clues ]
        else:
            raise OffNominal  # supporting only "clue" and [num, "clue"] forms

        # compute solution words and positions along with clue numbers
        self.parse_clues_soln(nums_only=1)
        if not solution:
            # real words not available; reset soln_words but keep soln_posns
            self.soln_words = None

# Additional fields (currently ignored, could be future additions):

# "publication": "HTML pub info"  Bibliographic reference for a published puzzle
# "url": "puzzle_url"             Permanent URL for the puzzle
# "uniqueid": "value"             Globally unique identifier for the puzzle
# "explanation": "HTML text"      Text displayed after successful solve
# "annotation": "text"            Non-displayed annotation
# "difficulty": "HTML text"       Informational only, there is no standard for difficulty
# "origin": "text"                Program-specific information from program that wrote this file
# "styles": { "name": StyleSpec, ... }      Named styles for the puzzle
# "checksum": [ "salt", "SHA1 hash", ... ]  Hashes for (correct solution + salt)

# "saved": [ [ CrosswordValue, ... ], ... ]  Current solve state of the puzzle
# "zones": [ GroupSpec, ... ]    Arbitrarily-shaped entries overlaid on the grid
# "zones": [ GroupSpec, ... ]    Arbitrarily-shaped entries overlaid on the grid
# "showenumerations": true/false    Show enumerations with clues
# "clueplacement": "before"/"after"/null    Where to put clues (null = auto)
# "clueplacement": "blocks"      Put clues in blocks adjacent to entry
# "answer": "entry"              The final answer to the puzzle
# "answers": [ "entry", ... ]    List of final answers to the puzzle
# "enumeration": Enumeration     Enumeration of the final answer to the puzzle
# "enumerations": [ Enumeration, ... ]    List of enumerations for final answers to the puzzle
# "misses": { "entry": "hint", ... }      List of hints to be given for misses

# HTML text fields:
# publisher, publication, title, intro, explanation, author, editor,
# notes, difficulty, clues


#-------------- Scanned clue list processing --------------

# Retrieve scanned clues from a text file or from the clipboard.
# OCR processing is presumed to have been done by the user, resulting
# in a plain text form of the clue lists.  To correct OCR mistakes,
# a window is displayed to allow the user to proofread and edit the
# clue lists.  Afterward, the clues are parsed to get the word
# numbers and clue text strings.

    def retrieve_clues(self, filename, puz_content):
        if filename:
            raw_clues = file(filename).readlines()    # can raise IOError
        else:
            raw_clues = puz_content.split('\n')
        extract = self.extract_clues(raw_clues, filename)
        if not extract:
            raise FalseStart
        self.format_type = 'scanned'
        self.nums =  [ [ c[0] for c in clues] for clues in extract[:2] ]
        self.clues = [ [ c[1] for c in clues] for clues in extract[:2] ]
        note_strings = extract[2]
        if extract[2]:
            note_strings += ['', '-----']
        note_strings += ['The puzzle clues were scanned and '
                         'imported from a printed source.']
        self.notes = [ s + '\n' for s in note_strings ]

        self.width, self.height = 0, 0       # will be overwritten later
        self.soln_grid = None
        self.soln_cksum = 0
        self.soln_flags = 0
        self.soln_words = None
        self.soln_posns = None
        self.title, self.author, self.copyright = '', '', ''
        self.symmetry_type = 'rot'

    def extract_clues(self, raw_clues, filename):
        raw_lines = \
            filter(None, [ ''.join([ c for c in s.strip()
                                     if c in string.printable ])
                           for s in raw_clues ])
        results = [0, None]
        widgets = [None, None, None, None]    # frame, raw, clean, errors
        done = BooleanVar()
        if root.winfo_screenheight() < 900: num_lines = 15
        else:                               num_lines = 20

        def show_clues(fr):
            tfr = Frame(fr)
            col1 = Frame(tfr)
            Label(col1, text='Raw text input for clues',
                  font=heading1_font).pack(pady=3)
            Label(col1, text=raw_clue_instructions,
                  justify=LEFT).pack(padx=5, pady=0)
            fr1, txt1 = scrolled_text_widget(col1, horiz_scroll=1,
                                             relief='sunken', border=1,
                                             width=50, height=num_lines)
            fr1.pack(side=TOP, padx=5, pady=5, expand=YES, fill=BOTH)
            Label(col1, text='Error messages',
                  font=heading1_font).pack(expand=NO)
            fr3, txt3 = scrolled_text_widget(col1, horiz_scroll=1,
                                             relief='sunken', border=1, 
                                             width=50, height=5)
            fr3.pack(side=TOP, padx=5, pady=5, expand=YES, fill=X)
            col1.pack(side=LEFT, expand=YES, fill=BOTH)

            col2 = Frame(tfr)
            Label(col2, text='Candidate clues after refining',
                  font=heading1_font).pack(pady=0)
            Label(col2, text=clue_editing_instructions,
                  justify=LEFT).pack(padx=5, pady=3)
            fr2, txt2 = scrolled_text_widget(col2, horiz_scroll=1,
                                             relief='sunken', border=1,
                                             width=50, height=num_lines+6)
            fr2.pack(side=TOP, padx=5, pady=5, expand=YES, fill=BOTH)
            col2.pack(side=LEFT, expand=YES, fill=BOTH)
            tfr.pack(padx=3, pady=3, expand=YES, fill=BOTH)
            for line in raw_lines:
                txt1.insert(END, line)
                txt1.insert(END, '\n')
            refine_clues((tfr, txt1, txt2, txt3))
            return tfr, txt1, txt2, txt3

        def validate_clues(fr):
            def sorry(*args):
                if args:
                    err_args = error_msg_sub('invalid_clue_specific', args)
                else:
                    err_args = error_messages['invalid_clues']
                widgets[3].delete('1.0', END)
                widgets[3].insert(END, err_args[1] + '\n')
            clue_text = \
                filter(None, [ c.strip() for c in
                               widgets[2].get('1.0', END).split('\n') ])
            try:
                a_start = clue_text.index('ACROSS')
                d_start = clue_text.index('DOWN')
                n_start = clue_text.index('NOTES')
            except ValueError:
                sorry()
                return False
            a_lines = filter(None, clue_text[a_start+1:d_start])
            d_lines = filter(None, clue_text[d_start+1:n_start])
            a_clues, d_clues = [], []
            for lines, clues, dir_text in \
                    ((a_lines, a_clues, 'Across'),
                     (d_lines, d_clues, 'Down')):
                prev, prev_clue = 0, dir_text
                for clue in lines:
                    try:
                        num, text = clue.split(None, 1)
                        num = int(num)
                    except ValueError:
                        sorry(dir_text, prev_clue + '\n' + clue + '\n')
                        return False
                    if prev >= num:
                        sorry(dir_text, prev_clue + '\n' + clue + '\n')
                        return False
                    clues.append((num, text))
                    prev = num
                    prev_clue = clue
            results[1] = (a_clues, d_clues, clue_text[n_start+1:])
            return True

        def refine_clues(txt_widgets=None):
            if not txt_widgets:
                # variable assigned after positioned_dialog executes
                txt_widgets = widgets
            raw_win, clean_win, err_win = txt_widgets[1:]
            err_win.delete('1.0', END)
            clean_win.tag_delete(*clean_win.tag_names())
            raw_lines = raw_win.get('1.0', END).split('\n')
            clean_plus_warn, notes_lines, error_msg = \
                clean_clues(filter(None, [ c.strip() for c in raw_lines ]))
            clean_win.delete('1.0', END)
            line_num, warnings = 1, []
            for line in clean_plus_warn:
                if line == '***warn***':
                    warnings.append(line_num)
                else:
                    clean_win.insert(END, line)
                    clean_win.insert(END, '\n')
                    line_num += 1
            clean_win.insert(END, '\nNOTES\n')
            for line in notes_lines:
                clean_win.insert(END, line)
                clean_win.insert(END, '\n')
            for w in warnings:
                tag = 'zone_%s' % w
                clean_win.tag_add(tag, '%d.0' % w, '%d.0' % (w + 2))
                clean_win.tag_config(tag, background=listbox_indicator)
            err_win.insert(END, error_msg)

        def accept_clues(fr):
            if not results[0]:   # user canceled
                results[1] = None
            done.set(1)
           
        fr, widgets = \
            positioned_dialog(root, results, use_grab=1,
                              use_cancel=1, cancel_default=1,
                              bind_return=0, close_text='Import',
                              other_buttons=(('Refine', refine_clues),),
                              default_button=0,
                              title="Proofread and edit clues -- %s"
                                    % os.path.split(filename)[1],
                              dialog_proc=show_clues,
                              validation_proc=validate_clues,
                              final_action=accept_clues,
                              width=0, height=0, )
        wrapped_bind(fr, '<Return>', None)
        root.wait_variable(done)
        return results[1]

# --- End of PuzzleDefn methods ---

def clean_clues(clue_text):
    def find_key(key):
        pattern = re.compile('.*(%s).*' % key)
        for n, line in enumerate(clue_text):
            key_match = pattern.match(line)
            if key_match:
                start, end = key_match.start(1), key_match.end(1)
                if start > 0: prev = line[:start]
                else:         prev = ''
                if end < len(line): next = line[end:]
                else:               next = ''
                return n, prev, key, next
        return -1, '', '', ''
    a_key = find_key('ACROSS')
    d_key = find_key('DOWN')
    if a_key[0] < 0 or d_key[0] < 0 or a_key[0] >= d_key[0]:
        return ([], [],
                'These clues are missing the headings ACROSS and '
                'DOWN.\nPlease repair or add the headings above, '
                'then click the\nRefine button to reprocess the clues. ')
    a_lines = clean_clue_list([a_key[3]] +
                              clue_text[ a_key[0]+1 : d_key[0] ] +
                              [d_key[1]])
    d_lines = clean_clue_list(clue_text[ d_key[0]+1 : ] + [d_key[3]])
    return ['ACROSS'] + a_lines + ['', 'DOWN'] + d_lines, \
           clue_text[0:a_key[0]], ''

# Parse an OCR-produced clue list and compensate for common errors.
# Search for numbers within lines that require splitting into two
# clues.  Join clue fragments split over several lines.  Check for
# parens to avoid recognizing numbers such as "(2 words)".

_word_num    = re.compile('(.*?)(\d+)\.?(?!-|\s*(wds|words))')
_open_paren  = re.compile('[^0-9)]*?\(')
_close_paren = re.compile('.*?\)')
_open_quote  = re.compile('\D*?"')
_close_quote = re.compile('.*?"')

def clean_clue_list(clue_list):
    if not clue_list: return []
    result = []
    clue_list = filter(None, clue_list)
    # OCR software can render underscores as tab characters:
    clue_list = [ clue.replace('\t', ' __ ') for clue in clue_list ]
    nesting, in_quote = 0, 0
    open_remaining = 0
    line_in = clue_list[0]
    num_match = _word_num.match(line_in)
    if num_match:
        line_out = num_match.group(2)
        prev_num = int(line_out)
        next = num_match.end(0)
    else:
        line_out = '1 '
        prev_num = 1
        next = 0
    next_line = 1

    while next_line < len(clue_list) or next < len(line_in):
        # line_out has the last recognized word number;
        # next is the char position immediately past that number.
        paren_match = _open_paren.match(line_in, next)
        if paren_match:
            nesting += 1
            open_remaining = 2
            line_out += paren_match.group(0)
            next = paren_match.end(0)
            continue
        if in_quote:
            quote_match = _close_quote.match(line_in, next)
            if quote_match:
                in_quote = 0
                if nesting == 0: open_remaining = 0
                line_out += quote_match.group(0)
                next = quote_match.end(0)
                continue
        else:
            quote_match = _open_quote.match(line_in, next)
            if quote_match:
                in_quote = 1
                open_remaining = 2
                line_out += quote_match.group(0)
                next = quote_match.end(0)
                continue
        if not (nesting or in_quote):
            num_match = _word_num.match(line_in, next)
            if num_match:
                new_num = int(num_match.group(2))
                if prev_num < new_num < prev_num + 20:
                    line_out += num_match.group(1)
                    result.append(line_out)
                    line_out = num_match.group(2)
                    prev_num = new_num
                else:
                    # non-word number; consume text so far
                    if prev_num - 20 < new_num <= prev_num or new_num == 1:
                        result.append('***warn***')    # suspicious number
                    line_out += num_match.group(0)
                next = num_match.end(0)
                continue
        paren_match = _close_paren.match(line_in, next)
        if paren_match:
            nesting = max(0, nesting - 1)
            line_out += paren_match.group(0)
            next = paren_match.end(0)
            if not in_quote: open_remaining = 0
            continue
        line_out += line_in[next:] + ' '
        if next_line >= len(clue_list): break
        next = 0
        line_in = clue_list[next_line]
        next_line += 1
        open_remaining -= 1
        if open_remaining == 0:
            # Force close in of case missing paren or quote.
            nesting, in_quote = 0, 0
            result.append('***warn***')
    if line_out:
        result.append(line_out)
    return result

raw_clue_instructions = \
    """This text shows the raw clues as interpreted by your OCR
software. Diagnil has tried to refine them, resulting in the
clues on the right. Further editing by hand might be needed
to create the final clue lists. Changes can be made to either
column. Click Refine if the text below has been edited.
"""
clue_editing_instructions = \
    """Proofread the clues below and edit as needed to correct any
residual scanning/OCR errors. Each clue should appear on a
separate line beginning with a valid word number. If desired,
you may append text at the end to go into the Notes section
of the puzzle file. Click Import when all editing is done.
"""

#-------------- HTML processing --------------

# Interpret lightweight HTML features (textual tags and entities).
# Used for ipuz format.  Since Tk widgets don't interpret HTML,
# just map tagged text fields into a plain-text rendering.
# Doesn't handle nested tags.  Also not handling &-entities for
# special characters.

def map_html(text):
    if '<' in text:
        text = _html_br_pattern.sub('\n', text)
        text = _html_tag_pattern.sub(render_tag, text)
    if '&' in text:
        text = _html_entity_pattern.sub(render_entity, text)
    return text

_html_br_pattern     = re.compile(r'<br[ \r\n\t]*/?>', re.IGNORECASE)
_html_tag_pattern    = re.compile(r'<(.+?)>(.*?)</\1>', re.IGNORECASE)
_html_entity_pattern = re.compile(r'&(.+?);', re.IGNORECASE)

_html_tag_mapping = dict(
    b      = ('<<<', '>>>'),
    i      = ('<<', '>>'),
    s      = ('///', '///'),
    u      = ('___', '___'),
    em     = ('<<', '>>'),
    strong = ('<<<', '>>>'),
    big    = ('++', '++'),
    small  = ('--', '--'),
    sup    = ('^', '^'),
    sub    = ('_', '_'),
    )
def render_tag(tag_match):
    prefix, suffix = _html_tag_mapping[tag_match.group(1)]
    return prefix + tag_match.group(2) + suffix

_html_entity_mapping = dict(
    quot   = '"',
    lt     = '<',
    gt     = '>',
    amp    = '&',
    )
def render_entity(entity_match):
    return _html_entity_mapping[entity_match.group(1)]

# HTML tags in ipuz spec:
# <b> ... </b>	Bold
# <i> ... </i>	Italic
# <s> ... </s>	Strikeout
# <u> ... </u>	Underline
# <em> ... </em>	Emphasis
# <strong> ... </strong>	Stronger emphasis
# <big> ... </big>	Bigger text
# <small> ... </small>	Smaller text
# <sup> ... </sup>	Superscript text
# <sub> ... </sub>	Subscript text
# <br> or <br/>	Line break (actually regex: <br[ \r\n\t]*/?> )

# &quot; Represents "
# &amp;	 Represents &
# &lt;	 Represents <
# &gt;	 Represents >
# Entities of the form &letters; are allowed for special and
# international characters. 


#-------------- Notes section processing --------------

# Try to infer the symmetry type by parsing the Notes section and looking
# for key phrases of the form '<adjective> symmetry'.

def infer_symmetry_type(puz_notes):
    notes = [ c.lower() for c in puz_notes
              if c.isalpha() or c.isspace() or c == '-' or c == '/']
    notes = ''.join(notes).split()
#    notes = ''.join(notes).replace('-', ' ').split()
    for word in notes:
        if word.startswith('asymmetric'):
            return None                    # absence of symmetry
    try:
        symm = notes.index('symmetry')
    except ValueError:
        # assume rotational if symmetry not mentioned in notes
        return 'rot'

    phrase = notes[symm-5:symm]    # grab relevant words
    for kind, keywords in \
            (('rot',   ('standard', 'regular', 'normal', 'rotational')),
             ('horiz', ('horizontal', 'left-to-right',
                        'left-right', 'left/right')),
             ('vert',  ('vertical', 'top-to-bottom',
                        'top-bottom', 'top/bottom')),
             ('ul-lr', ('upper-left', 'lower-right')),
             ('ur-ll', ('upper-right', 'lower-left')),
             ):
        for word in keywords:
            if word in phrase:
                return kind        # match -- found symmetry type

    # No was match found, meaning the author is using adjectives not listed
    # above.  Assume standard symmetry simply because it's the most common.
    # User can correct type as needed.
    return 'rot'


#-------------- Scrambling/unscrambling --------------

# The following code is adapted from the snippets posted by Mike Richards.

# Argument soln is the puzzle's solution formatted as a single string.
# It is formed by concatenating all the columns left to right, that is,
# a traversal that runs down instead of across.  Black squares are
# skipped in the traversal.  For example, if the puzzle solution is:
#     A B C
#     : : D
#     E F G
# the soln input string is AEBFCDG.  "Key" is a list of 4 digits.

# The resulting scrambled solution will replace the real solution
# after re-inserting the black squares, e.g., scrambling the puzzle
# above with key 1234 produces:
#   scramble('AEBFCDG', [1,2,3,4]) -> 'MLOOPKJ'
# turning the solution grid into:  M O P
#                                  : : K
#                                  L O J
# The unscrambling algorithm is exactly the opposite of the scrambling
# algorithm and uses the same string representation.

def scramble(soln, key):
    scrambled = soln
    for key_num in key:
        last_scramble = scrambled
        scrambled = ''
        for i, letter in enumerate(last_scramble):
            letter_val = ord(letter) + key[i % 4]
            # Make sure this letter is a capital letter
            if letter_val > 90:
                letter_val -= 26
            scrambled += chr(letter_val)
        scrambled = rotate_left(scrambled, key_num)
        scrambled = shuffle_string(scrambled)
    return scrambled

def rotate_left(string, num):
    return string[num:] + string[:num]

def shuffle_string(scrambled):
    # Split the string in half
    mid = len(scrambled) / 2
    front = scrambled[:mid]
    back = scrambled[mid:]
    # Assemble the parts:
    # back[0], front[0], back[1], front[1] . . .
    return_str = ''
    for f, b in zip(front, back):
        return_str += b + f
    # If len(scrambled) is odd, the last character got left off
    if len(scrambled) % 2 != 0:
        return_str += back[-1]
    return return_str


# Unscrambling just inverts all the steps above in reverse order.

def unscramble(locked, key):
    unscrambled = locked
    for key_num in reversed(key):
        unscrambled = unshuffle_string(unscrambled)
        unscrambled = rotate_right(unscrambled, key_num)

        last_unscr = unscrambled
        unscr = []
        # generate indexes, letters in reverse of scrambling order
        for i, letter in zip(range(len(last_unscr)-1, -1, -1),
                             reversed(last_unscr)):
            letter_val = ord(letter) - key[i % 4]
            # Make sure this letter is a capital letter
            if letter_val < 65:
                letter_val += 26
            unscr.append(chr(letter_val))
        unscr.reverse()
        unscrambled = ''.join(unscr)
    return unscrambled

def rotate_right(string, num):
    return string[-num:] + string[:-num]

def unshuffle_string(scrambled):
    # If len(scrambled) is odd, the last character was not shuffled
    if len(scrambled) % 2 != 0:
        tail = [scrambled[-1]]
        limit = len(scrambled) - 1
    else:
        tail = []
        limit = len(scrambled)
    # undo the shuffle back[0], front[0], back[1], front[1], ...
    # to recreate front and back halves of original string
    front, back = [], []
    for i in range(0, limit, 2):
        back.append(scrambled[i])
        front.append(scrambled[i+1])
    full = front + back + tail
    return ''.join(full)


#-------------- Checksums --------------

def cksum_region(region, cksum):
  for c in region:
      if cksum & 0x0001:
          cksum = (cksum >> 1) | 0x8000
      else:
          cksum = cksum >> 1
      cksum += ord(c)
  return cksum

# Code above is the Python implementation of this C version:

# unsigned short cksum_region(unsigned char *base, int len,
#                             unsigned short cksum) {
#   int i;
#   for (i = 0; i < len; i++) {
#     if (cksum & 0x0001)
#       cksum = (cksum >> 1) + 0x8000;
#     else
#       cksum = cksum >> 1;
#     cksum += *(base+i);
#   }
#   return cksum;
# }
