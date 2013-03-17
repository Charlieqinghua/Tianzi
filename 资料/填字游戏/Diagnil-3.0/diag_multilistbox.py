# The following class is an adaptation and extension of
#   Recipe 52266: MultiListbox Tkinter widget (Python) by Brent Burley
#   http://code.activestate.com/recipes/52266-multilistbox-tkinter-widget/


from diag_globals import *
from textwrap     import wrap, TextWrapper

scroll_incr = 5


# The MultiListbox class introduces two types of multiplicity for
# listboxes, retaining the same interface as regular listboxes.  In the
# first type, a ganged array of several listboxes are packed left to right,
# having a vertical scrollbar on the right.  Each can have an optional
# header at the top and an optional horizontal scrollbar on the bottom.
# Events are applied to all listboxes so each experiences the same motion.
# Only SINGLE selection mode is supported.  The second type is to allow
# multi-line items with word wrapping.  The number of lines in an item is
# determined dynamically based on how the words fit.  Both types of 
# multiplicity can be used simultaneously.
#
# Currently, string-based index values are limited to END ('end');
# 'active', 'anchor', and '@x,y' are not supported.
# A lot of overhead is used to implement the multi-line feature so
# this class would not be best if only multiple columns are needed.
# Also, it likely will be inefficient for listboxes with more than
# 100 or so items.


class MultiListbox(Frame):
    # columns is a sequence of listbox descriptors;
    # each is a tuple of the form:
    # (padding, option_dict) or:
    # (header, width, expand_weight, horiz, option_dict)
    # padding indicates the width for an empty column
    # horiz is 'wrap' for word wrapping,
    # 'hbar' for horizontal scrollbar,
    #   or ''/None for neither

    def __init__(self, master, FlatScrollbar,
                 select_action=None, barwidth=14,
                 columns=(('', 30, 1, None, {}), ('', 30, 1, None, {})),
                 **box_options):
        listbox_options = \
            merged_options(box_options, selectmode=SINGLE, exportselection=0)
        self.columns = columns
	Frame.__init__(self, master)
        scrollbar = FlatScrollbar(self, command=self._scroll, width=barwidth)
	self.boxes = []
        # if all headers are empty, omit header row:
        use_headers = filter(None, [ c[0] for c in columns
                                     if isinstance(c[0], basestring) ])

        self.indices = range(len(columns))
        self.char_width = []
        self.font = []
        self.item_len   = []   # used to compute abstract index
        self.index_incr = []   # used to compute concrete index;
                               # 1 in last row of item; 0 elsewhere
	for col_num, descriptor in enumerate(columns):
	    frame = Frame(self)
            if isinstance(descriptor[0], int):
                header, width, weight, horiz, options = \
                    '', descriptor[0], 0, 0, descriptor[1]
            else:
                header, width, weight, horiz, options = descriptor

            if horiz == 'wrap':
                col_font = tkFont.Font(root=root, font=lb['font'])
            else:
                col_font = None
            self.font.append(col_font)

            if use_headers:
                Label(frame, text=header, borderwidth=1,
                      relief=RAISED).pack(fill=X)
	    lb = Listbox(frame,
                         **merged_options(options, borderwidth=0,
                                          selectborderwidth=0, relief=FLAT,
                                          **listbox_options))
            lb['width'] = width    # set after font applied
	    lb.pack(expand=YES, fill=BOTH)
	    self.boxes.append(lb)
            self.char_width.append(width)

            if select_action == None:
                def select_proc(e, s=self):
                    s._select(e.y)
            else:
                def select_proc(e):
                    select_action(e)
                    # suppress default Listbox selection because it
                    # overwrites the multi-item selection
                    return 'break'

	    wrapped_bind(lb, '<B1-Motion>', select_proc, 'Multilistbox')
	    wrapped_bind(lb, '<Button-1>',  select_proc, 'Multilistbox')
	    wrapped_bind(lb, '<Leave>',     lambda e: 'break', 'Multilistbox')
#	    lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
#	    lb.bind('<Button-2>',  lambda e, s=self: s._button2(e.x, e.y))

            if on_osx:
                wrapped_bind(lb, '<MouseWheel>',
                             lambda e, s=self:
                                 s._scroll('scroll', -e.delta, UNITS))
            elif on_win:
                pass        # bindings applied at app level
            else:
                # mouse wheels for Linux and X-windows systems:
                wrapped_bind(lb, '<Button-4>',
                             lambda e, s=self:
                                 s._scroll('scroll', -scroll_incr, UNITS))
                wrapped_bind(lb, '<Button-5>',
                             lambda e, s=self:
                                 s._scroll('scroll', scroll_incr, UNITS))

            if horiz == 'hbar':
                hscroll = FlatScrollbar(self, command=lb.xview,
                                        width=barwidth, orient=HORIZONTAL)
                lb.configure(xscrollcommand=hscroll.set)
                hscroll.grid(row=1, column=col_num, sticky='ew')
                self.rowconfigure(1, weight=0, minsize=0)
            frame.grid(row=0, column=col_num, sticky='news')
            self.columnconfigure(col_num, weight=weight, minsize=0)

        scrollbar.grid(row=0, column=col_num+1, sticky='ns')
        self.rowconfigure(0, weight=1, minsize=0)
        self.columnconfigure(col_num+1, weight=0, minsize=0)
	self.boxes[0]['yscrollcommand'] = scrollbar.set


# Text wrapping is provided for long strings.  Variable-width fonts are
# accommodated for a tighter fit.  Strings and their wrapped counterparts
# are cached to reduce the overhead of rebuilding a listbox.
# This method was broken out, splitting the initialization into two parts.
# This second part needs to be invoked after the widgets are built and
# packed so the actual listbox widths are established.

    def set_multilistbox_wrappers(self):
        self.wrapper = []
	for col_num, descriptor in enumerate(self.columns):
            if isinstance(descriptor[0], int):
                header, width, weight, horiz, options = \
                    '', descriptor[0], 0, 0, descriptor[1]
            else:
                header, width, weight, horiz, options = descriptor

            if horiz == 'wrap':
                req_width = self.boxes[col_num].winfo_reqwidth()
                # winfo_width might not be set to its final value
                # immediately; sample it every 100ms for about 2 seconds
                for i in range(20):
                    box_width = self.boxes[col_num].winfo_width()
                    if box_width >= req_width:
                        break          # width is ready now
                    root.update_idletasks()
                    time.sleep(0.1)    # else, wait for window system events
                else:
                    box_width = req_width   # not done, give up

                if on_win or on_osx:
                    pwidth = box_width - 2
                else:
                    # font metrics on Linux can be inaccurate; reduce width
                    # to ensure an adequate fit
                    pwidth = int(box_width * 0.8)
                self.wrapper.append(VarTextWrapper(self.font[col_num], pwidth))
            else:
                self.wrapper.append(None)


    def _button2(self, x, y):
	for b in self.boxes: b.scan_mark(x, y)
	return 'break'

    def _b2motion(self, x, y):
	for b in self.boxes: b.scan_dragto(x, y)
	return 'break'

    def _scroll(self, *args):
	for b in self.boxes:
	    apply(b.yview, args)
        # suppress binding for listbox under mouse cursor
        # to prevent double scrolling:
        return 'break'

    def _abstract_index(self, index):
        # map listbox index from concrete index to abstract index
        # to account for multi-line items
        if isinstance(index, basestring):
            index = self.boxes[0].index(index)
        return sum(self.index_incr[:index])

    def _concrete_index(self, index):
        # map listbox index from abstract index to concrete index
        # to account for multi-line items
        if isinstance(index, basestring):
            if index == END:
                return len(self.index_incr)
            else:
                raise ValueError     # active, anchor, @x,y not supported
        return sum(self.item_len[:index])

    def _concrete_first_last(self, first, last=None):
        # given abstract first and last indices, derive concrete counterparts
        cfirst = self._concrete_index(first)
        if last == None:
            clast = cfirst + self.item_len[first] - 1
        elif last == END:
            clast = len(self.index_incr)
        else:
            clast = self._concrete_index(last) + self.item_len[last] - 1
        return cfirst, clast

    def _select(self, y):
	row = self._abstract_index(self.boxes[0].nearest(y))
	self.selection_clear(0, END)
	self.selection_set(row)
	return 'break'

        
# The following methods implement analogs of the corresponding methods
# in the Listbox class.  See the Tkinter module for documentation.

    def activate(self, index):
        # due to Tk listbox design, only first line can be activated
        cindex = self._concrete_index(index)
	for b in self.boxes:
	    b.activate(index)
	return 'break'

#    def bbox(self, *args):

    def bind(self, event, proc):
	for b in self.boxes: b.bind(event, proc)

    def curselection(self):
        # multiple concrete rows can be selected for one abstract row
        sel = self.boxes[0].curselection()
        if sel:
            return (self._abstract_index(sel[0]),)
        else:
            return sel

    def delete(self, first, last=None):
        # derive concrete index values and delete corresponding items
        try:
            cfirst, clast = self._concrete_first_last(first, last)
        except IndexError:
            return 'break'      # index range doesn't exist
        if last == None:
            last = first
        elif last == END:
            last = len(self.item_len) - 1
        del self.item_len[first:last+1]
        del self.index_incr[cfirst:clast+1]
	for b in self.boxes:
	    b.delete(cfirst, clast)
	return 'break'

    def get(self, first, last=None):
        if last == None:
            last = first
        elif last == END:
            last = len(self.item_len) - 1
	result = []
        for index in range(first, last+1):
            cfirst, clast = self._concrete_first_last(index, None)
            row = []
            for b in self.boxes:
                item = b.get(cfirst, clast)
                # Tkinter or Tk returns (inconsistently) either
                # a single string or a tuple of strings
                if isinstance(item, tuple):
                    item = ' '.join(filter(None, item))
                row.append(item)
            result.append(tuple(row))
	return result  # tuple instead of list?
	    
    def index(self, index):
        index = self.boxes[0].index(index)
        if index < 0: return index
	else:         return self._abstract_index(index)

    def insert(self, index, *elements):
        # each element is a tuple of values, one for each column
        cindex = self._concrete_index(index)
        if index == END:
            index = len(self.item_len)
	for values in elements:
            strings = []               # one for each column
            for v in values:
                if isinstance(v, basestring):
                    strings.append([v])
                else:
                    strings.append(v)  # list: previously wrapped string

            max_len = max(map(len, strings))
            for b, s in zip(self.boxes, strings):
                s.extend([''] * (max_len - len(s)))
                b.insert(cindex, *s)
            self.item_len.insert(index, max_len)
            self.index_incr[cindex:cindex] = [0] * (max_len - 1) + [1]
            index += 1
	return 'break'

    def nearest(self, y):
        index = self.boxes[0].nearest(y)
        if index < 0: return index
        else:         return self._abstract_index(index)

#    def scan_mark(self, x, y):
#    def scan_dragto(self, x, y):

    def see(self, index):
        cfirst, clast = self._concrete_first_last(index)
	for b in self.boxes:
            # try both first and last concrete items to ensure entire
            # multiline item is seen
	    b.see(cfirst)
	    if clast > cfirst: b.see(clast)
	return 'break'

    def selection_anchor(self, index):
        cindex = self._concrete_index(index)
	for b in self.boxes:
	    b.selection_anchor(cindex)
	return 'break'

    def selection_clear(self, first, last=None):
        cfirst, clast = self._concrete_first_last(first, last)
	for b in self.boxes:
	    b.selection_clear(cfirst, clast)
	return 'break'

    def selection_includes(self, index):
        cindex = self._concrete_index(index)
	return self.boxes[0].selection_includes(cindex)

    def selection_set(self, first, last=None):
        cfirst, clast = self._concrete_first_last(first, last)
	for b in self.boxes:
	    b.selection_set(cfirst, clast)
	return 'break'

    def size(self):
	return len(self.item_len)

#    def xview(self, *what):
#    def xview_moveto(self, fraction):
#    def xview_scroll(self, number, what):

    def yview(self, *what):
        if what:
            index = self._concrete_index(what[0])
            for b in self.boxes:
                b.yview(index)
        else:
            return self.boxes[0].yview()

    def yview_moveto(self, fraction):
        for b in self.boxes:
            b.yview_moveto(fraction)
	return 'break'

    def yview_scroll(self, number, what):
        ### consider making abstract item the scrolling unit
        for b in self.boxes:
            b.yview_scroll(number, what)
	return 'break'

#    def itemcget(self, index, option):

    def itemconfigure(self, index, cnf=None, **kw):
        cfirst, clast = self._concrete_first_last(index, index)
        item_range = range(cfirst, clast + 1)
        for b in self.boxes:
            for i in item_range:
                b.itemconfigure(i, cnf=cnf, **kw)
	return 'break'

    def itemconfigurecolumn(self, index, column, cnf=None, **kw):
        cfirst, clast = self._concrete_first_last(index, index)
        item_range = range(cfirst, clast + 1)
        b = self.boxes[column]
        for i in item_range:
            b.itemconfigure(i, cnf=cnf, **kw)
	return 'break'


    def wrap_string(self, col, string):
        return self.wrapper[col].wrap(string)



#==================

# Following is a refinement of the algorithm in Python library textwrap.
# It allows a tighter fit for variable-width fonts by estimating actual
# character widths.  This function overrides the corresponding function
# in the TextWrapper class from that library.

class VarTextWrapper(TextWrapper):
    def __init__(self, font, pixel_width, *args, **kwargs):
        TextWrapper.__init__(self, *args, **kwargs)
        self.font = font
        self.pixel_width = pixel_width
        # find widths of the printable ASCII characters
        self.char_pwid = [0] * 32 + \
                         [ font.measure(chr(n)) for n in range(32, 127) ]
        self.max_pwid = max(self.char_pwid)
        # map all non-ASCII characters (Unicode) to max width
        self.char_pwid.append(self.max_pwid)
        self.uchar_pwid = {}
        for c in (null_word_symb, clue_separator):
            self.uchar_pwid[ord(c)] = font.measure(c)

    def _chunk_width(self, chunk):
        # account for control chars (< 32)
        codes = map(ord, chunk)
        awidths = [ self.char_pwid[c] for c in codes if c < 127 ]
        uwidths = [ self.uchar_pwid.get(c, self.max_pwid)
                    for c in codes if c >= 127 ]
        return sum(awidths) + sum(uwidths)
#        return self.font.measure(chunk)

    def _wrap_chunks(self, chunks):
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)

        # Arrange in reverse order so items can be efficiently popped
        # from a stack of chucks.
        chunks.reverse()

        while chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len is just the length of all the chunks in cur_line.
            cur_line = []
            cur_len  = 0
            cur_plen = 0     # length in pixels for designated font

            # Figure out which static string will prefix this line.
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - len(indent)
            pixel_width = self.pixel_width - self._chunk_width(indent)

            # First chunk on line is whitespace -- drop it, unless this
            # is the very beginning of the text (ie. no lines started yet).
            if chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = len(chunks[-1])
                pl = self._chunk_width(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_plen + pl <= pixel_width:
                    cur_line.append(chunks.pop())
                    cur_len += l
                    cur_plen += pl

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and pl > pixel_width:
                self._handle_long_word(chunks, cur_line, cur_len, width)

            # If the last chunk on this line is all whitespace, drop it.
            if cur_line and cur_line[-1].strip() == '':
                del cur_line[-1]

            # Convert current line back to a string and store it in list
            # of all lines (return value).
            if cur_line:
                lines.append(indent + ''.join(cur_line))

        return lines
