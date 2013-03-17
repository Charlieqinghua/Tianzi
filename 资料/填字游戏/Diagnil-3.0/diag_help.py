# Text sections of User's Guide

# Each help topic has the form (topic-name, section, ...).  Each section
# is either a string or a tuple (S1, ..., Sn).  Tuples denote image items;
# each Si is either a string label or an image file name (gif format).
# HTML-like tags of the form <<tag::text>> may be inserted in strings.


helpItems = (
    
('Introduction' ,
"\n\
<<heading1::Diagnil: Diagramless Crossword Assistant  	     Version 3.0>> \
\n\n\
Welcome to Diagnil, a tool for diagramless crossword enthusiasts. \
Diagnil helps you solve puzzles distributed in paper form or \
those distributed electronically using a supported file format \
(currently, Across Lite, Crossword Solver, XPF and ipuz). \
\n\n\
To solve puzzles in print form, all you need are lists of \
word clues obtained from books, newspapers or \
other sources. \
To solve puzzles rendered in electronic form, \
you need to obtain files that have been specifically prepared as \
diagramless puzzles in <<bold::puz, jpz, xpf>> or <<bold::ipuz>> format. \
Alternatively, Diagnil allows you to solve standard crosswords in these \
formats as if they were diagramless. \
\n\n\
Select a topic from the list on the left to \
view a description of the corresponding features. \
If you're a new user, begin with the Outline. \
Consult the more detailed topics as needed. \
If you're completely new to diagramless crosswords, you might want \
to look at the <<topic::Diagramless Primer>> \
(under the application Help menu). \
\n\n\
The main Diagnil web site is located at: \
\n\n    <<blue::http://blueherons.org/diagnil/>> \
\n\n\
Diagnil is open-source software ('BSD-style' license). \
You may use and redistribute it freely. \
\n\n\n\
Ben Di Vito  <bdivito@cox.net> \
\n\
Yorktown, Virginia \
\n\
August 2012 \
" ) ,

('Outline of Topics' ,
"<<heading1::1.  Basic Operation>> \
\n\n\
Basic operation and commands are described in this section. \
You should be ready to use Diagnil after reading or scanning \
the following topics. \
\n\n\
	Modes of Operation \n\
	Application Menu \n\
	Entering Words \n\
	Grid Navigation \n\
	Edit Menu Commands \n\
	View Menu Commands \n\
	Grid Commands \n\
\n\
<<heading1::2.  Word Entry Shortcuts>> \
\n\n\
After gaining some experience with the operations described above, \
you might find these more advanced features useful. \
\n\n\
	Moving Words \n\
	Word Number Aids \n\
	Word Letter Aids \n\
	Alternative Answers \n\
	Word Search \n\
\n\
<<heading1::3.  Other Features>> \
\n\n\
These features concern the control of Diagnil's behavior \
and working with puzzle files. \
\n\n \
	Grid Symmetry \n\
	Completeness Criteria \n\
	Preference Settings \n\
	Crossword File Formats \n\
	Importing Scanned Clues \n\
	Miscellaneous Notes \n\
\n\
<<heading1::4.  Suggestions for Puzzle Solving>> \
\n\n\
Although you will no doubt develop your own style, a few ideas \
on how to approach puzzle solving are collected here. \
\n\n \
	Getting Started \n\
	Placing Words \n\
	Using Minigrids \n\
	Additional Tips \n\
\n\
" ) ,

('Modes of Operation' ,
"Diagnil supports two modes for clue handling \
and two modes for grid navigation. \
The choice of clue mode is determined by how you start a new puzzle, \
as explained on the <<topic::Application Menu>> page. \
The grid navigation mode is chosen via a preference setting. \
\n\n\
In <<bold::clueless mode>>, you're solving a puzzle whose clues are only \
available on paper or some printable file format such as PDF. \
Building a diagramless solution with Diagnil's help \
saves you the erasure-prone difficulties of working on paper. \
\n\n\
In contrast, <<bold::clueful mode>> occurs when you open a puzzle prepared \
for computer-based solving using a supported file format \
such as Across Lite. \
By convention, files in this format have names ending with the \
extension '.puz'. \
Diagnil also supports the Crossword Solver (.jpz) format \
as well as two newer file formats: XPF and ipuz. \
See the section on <<topic::Crossword File Formats>> for additional details. \
\n\n\
If <<bold::keyboard-based grid navigation>> is selected, keystroke commands \
are provided for moving a cursor around the grid. \
This operating style is similar to that used by standard crossword \
solvers such as Across Lite, Crossword Solver, Java applets, etc. \
Users experienced with these applications would likely prefer the \
analogous style when using Diagnil. \
The alternative is <<bold::mouse-based grid navigation>>, \
where the location of \
the mouse cursor determines where actions take place. \
Some users might find this style more effective. \
\n\n\
If you're a regular user of Across Lite or similar crossword \
solvers, be aware that even with key-based navigation, \
using Diagnil differs in significant ways. \
The most important difference concerns how letters \
are entered on the grid. Instead of placing individual letters on \
the grid as you type them, Diagnil collects letters into words and \
uses <<bold::word-based features>> to fill the grid. \
With diagramless puzzles, being able to move items \
on the grid is important. \
Selecting and moving individual letters \
would be awkward, so words and groups of words are the basic \
units of grid manipulation. \
Please be patient -- these differences in operating style serve a purpose. \
" ) ,

('Application Menu' ,
"The menu bar in the Diagnil application window \
offers the usual File operations plus a few other \
operations under Edit and View. \
Control-key accelerators are available to invoke some actions. \
\n\n\
Selecting the New menu item starts a new puzzle in clueless mode. \
Selecting the Open menu item and choosing a '.puz' file \
(or .jpz, .xpf, .ipuz file) starts a new \
puzzle in clueful mode. You will see the lists of clues appear in the \
two boxes on the right side of the Diagnil window. \
If the file is not known to be a diagramless puzzle, you will be \
asked if you'd like to open it anyway. \
\n\n\
A list of recently opened puzzle files is maintained and selectable \
from the File menu. Use the Ctrl-Cmd-I key combination to \
reopen the most recently opened file. \
After opening a puzzle, a timer will be started and \
displayed on the status line. \
\n\n\
Diagnil saves intermediate versions of your puzzle solution using its \
own <<bold::file format>> where files have names \
ending with the extension <<bold::'.dg0'>> \
(D-G-zero). \
Once a new puzzle has been imported from a file rendered in a \
supported format ('.puz', '.jpz', '.xpf', '.ipuz'), the puzzle is saved \
to a '.dg0' file, after which \
the puz/jpz/xpf/ipuz file is no longer needed \
(its clues and other information are copied). \
Any previously saved puzzle in the form of a '.dg0' file \
may be resumed using the Open menu item. \
\n\n\
Installation on Windows or Mac OS X should create \
appropriate <<bold::file associations>> \
so that double-clicking a file of type '.dg0' starts Diagnil and \
opens the file. If a file association was not created, you can normally \
establish one manually. Although the method varies by operating system, \
typically it involves right-clicking on the file to pop up a menu, \
selecting Open With (or equivalent), \
then choosing the Diagnil application for invocation. \
After that, the system should associate the '.dg0' file type with the \
Diagnil application. \
\n\n\
If you've completed some puzzles whose files you no longer wish to save, \
you may delete them selectively using the \
Delete Puzzles menu item. \
" ) ,

('Entering Words' ,
u"Unlike other crossword solvers, Diagnil keeps separate answer lists \
in addition to rendering words on the grid. This gives you \
the flexibility to enter a word first on the Across/Down list, \
then paste it on the grid later. \
\n\n\
<<heading1::Clueful Mode>> \
\n\n\
The word list boxes will be filled with clues \
when a new puzzle is started. \
A typical list item will have this form: \
\n\n\
	32  - \N{white square} \N{black diamond} Four-legged honey fanciers \n\
\n\
The white square indicates an answer has yet to be entered while the \
black diamond merely separates the answer from the clue. \
To enter a word, simply select a clue on the list and type the word. \
<<bold::Pressing the Enter key>> or clicking on the Enter button records \
the word in the list box below. The resulting list item becomes: \
\n\n\
	32  - bears \N{black diamond} Four-legged honey fanciers \n\
\n\n\
<<heading1::Clueless Mode>> \
\n\n\
The word list boxes will be empty when a new puzzle \
is started. Words are entered by first moving the mouse cursor over either \
word list panel and then typing an entry such as '32 bears' \
(the quotes are not typed). Spaces may be omitted, as in '32bears'. \
In most cases the number may be omitted; see the page on \
<<topic::Word Number Aids>>. \
\n\n ",
('\t\t', 'enter-word.gif', '      Clueless word entry') ,

u"<<bold::Pressing the Enter key>> or clicking on the Enter button records \
the word in the list box below. \
Every word that you enter will be inserted in these lists in \
proper numerical order. After entry, \
a typical word list item will appear in this form: \
\n\n\
	32  - bears \n\
\n\
The minus sign indicates that the word has not yet been placed on the grid. \
\n\n\
<<heading1::Both Modes>> \
\n\n\
It suffices to move the mouse cursor \
over a panel to give it the <<bold::keyboard focus>>, which is indicated by \
highlighting around the text entry box (or a flashing insertion cursor) \
and an arrow cursor when the mouse is over the grid area. \
To <<bold::paste a word on the grid>> (in either mode), \
select it from the word list, then move \
the mouse/key cursor over the desired cell and press Enter. \
To <<bold::combine entry and placement>> in one step, \
place the mouse/key cursor at the desired starting cell, \
type the letters of the new word, then press Enter. \
Black squares (gray, actually) will be added \
automatically to both ends of a word when it is placed on the grid. \
\n\n ",
('\t\t', 'enter-paste.gif', '      Grid placement') ,

u"Selecting a word from the word list allows you to edit and reenter it, \
or to delete it using the Delete button. Words not yet placed on \
any grid are colored dark red and marked with a '-' in the word lists; \
those placed on the main grid are marked with a '+'. \
\n\n\
Some checks are made to prevent you from placing words at locations \
that conflict with other words or black squares. \
<<bold::Crossing-word clashes>> \
(two different letters in the same cell) \
are allowed and marked with a red dot in the lower right corner \
of the cell. You may leave clashes intact and resolve the conflicts later. \
\n\n\
After a word is entered, letters in the crossing direction \
and those next to the new word are checked \
to see if any additional words appear to be complete. \
If so, they will be entered automatically. \
Also, a check is performed (in clueful mode) \
to see if the entire puzzle is now complete. \
If so, the puzzle will be <<bold::finalized automatically>>. \
" ) ,

('Grid Navigation' ,
"<<heading1::Mouse-Based Navigation>> \
\n\n\
Diagnil allows you to navigate around the grid using a simple \
mouse-based approach. Word entry and other actions occur at the \
cell under the <<bold::mouse cursor>>. \
Usually this is assumed to be the location \
for the first letter of a word. Pressing the Enter key causes a typed or \
selected word to be pasted at the mouse cursor's location. \
<<bold::Clicking the left mouse button>> has the \
<<bold::same effect as the Enter key>> \
while also allowing you to preview a word and drag it around the grid \
before settling on a final location. \
Placing the next word on the grid is a simple matter of moving \
the mouse cursor to a new location. \
\n\n\
While this method is convenient in many ways, it has some drawbacks. \
For good typists, switching frequently between mouse and keyboard \
can reduce efficiency. When word-entry actions can be chained from one word \
to the next adjacent one, stopping to move the mouse cursor \
to a nearby cell might slow down the solving process. \
Key-based navigation offers improvements in this regard, although it can be \
less effective in the early solving phase when the grid is sparsely filled. \
\n\n\
Mouse navigation mode can be enabled and disabled using the \
Session Settings menu item on the Edit menu. \
It also can be enabled by default as a user preference. \
\n\n\
<<heading1::Key-Based Navigation>> \
\n\n\
Users having experience with solving tools \
for standard crosswords (e.g., Across Lite or Crossword Solver), \
might prefer the keystroke-based approach to grid navigation. \
As of version 3.0, Diagnil provides a grid navigation mode that \
enables use of the arrow keys and the Tab key. This mode reduces \
the need to perform actions with the mouse, allowing you to spend \
more time with your hands on the keyboard. \
\n\n\
When enabled, key navigation mode places a <<bold::key cursor>> \
on the grid, shown as a light blue pointer shaped like home plate. \
\n\n ",
('\t\t', 'Key-based word entry cursor:      ', 'key-cursor.gif') ,

u"For word entry purposes, the position of the key cursor \
is where the first letter of a word will be placed. \
\n\n\
Several commands are provided to manipulate the cursor: \
\n\n\
	\N{bullet} <<bold::Right Arrow:>> \
move the key cursor one cell to the right; \
set working direction to Across. \n\n\
	\N{bullet} <<bold::Shift-Right Arrow:>> \
move the key cursor one cell to the \
right; retain current working direction. \n\n\
	\N{bullet} <<bold::Left/Up/Down Arrow:>> \
move the key cursor as indicated; \
set working direction. \n\n\
	\N{bullet} <<bold::Shift-Left/Up/Down Arrow:>> \
move the key cursor as \
indicated; retain working direction. \n\n\
	\N{bullet} <<bold::Tab:>> \
move the key cursor to the start of the next word \
in the current direction. If no word is nearby, move a short distance \
(usually four squares). \n\n\
	\N{bullet} <<bold::Shift-Tab:>> \
move the cursor as for Tab, \
except in the reverse direction. \n\n\
	\N{bullet} <<bold::Left-Click:>> \
place the key cursor at the cell currently \
under the mouse cursor. \n\
\n\
To <<bold::toggle working direction>> at the same time you click the \
left mouse button, a short <<bold::mouse gesture>> \
can be used. When you click in a cell, hold the mouse button \
down and drag the mouse cursor to the next cell rightward or downward, \
then release the button. \
This will change the current direction to Across or Down. \
\n\n\
Although words are entered and placed on the grid using the location of \
the key cursor, \
the <<bold::mouse cursor must lie over the grid>> to enable placement. \
When you type the letters for a word, they will be previewed at the \
key cursor location. \
Pressing the Enter key will place the word in those same cells. \
If you would prefer to place the word at a different site, you can \
use the arrow commands to move the key cursor, then press Enter \
when the desired site is reached. \
" ) ,

('Edit Menu Commands' ,
"Actions that make a permanent change to the puzzle can be undone \
using the Undo button (or its equivalent on the Edit menu or \
the Ctrl-Cmd-Z key combination). Up to ten steps (or more, by changing \
a preference setting) can be undone. Undo only works within \
a single session; once the program terminates, previous steps \
will not be remembered. \
If you Undo too many steps, use Redo (Ctrl-Cmd-Y) to recover. \
\n\n\
A few commands require a sequence of two or three mouse clicks \
to manipulate regions on the grid. Abort Multistep Action (Esc) is provided \
to terminate such commands before all mouse clicks have been entered. \
It can also be used in other cases to cause a reset. \
\n\n\
Immediately after entering a word you might realize you've made \
a mistake and need to edit it. The Recall Last Entry (Ctrl-Cmd-L) item \
on the Edit menu retrieves the word for editing. \
\n\n\
In clueless mode you might inadvertently enter a word on the \
Across list and need to move it to the Down list (or vice versa). \
Simply select the word \
from its list and click the Rotate Word (Ctrl-Cmd-R) item on the Edit menu. \
\n\n\
The Find Word menu item invokes a feature described \
in Help topic <<topic::Word Search>>. \
\n\n\
After all words have been placed on the main grid, you may select \
Finalize Puzzle on the Edit menu. (Finalization normally happens \
automatically in clueful mode.) This command determines \
the puzzle's boundaries, fills in black squares as needed, then moves \
the completed puzzle, if necessary, to the upper left corner of the grid. \
No further changes to the puzzle will be allowed after finalization; \
it is considered frozen. \
Use Undo to restore the puzzle to its unfinished (and editable) state. \
\n\n\
If you're working on a puzzle created with the Import Clues feature \
(described in Help topic <<topic::Importing Scanned Clues>>), \
and you find you need to make corrections, the Edit Imported Clues \
menu item allows you to add, modify or delete individual clues. \
If you want to edit an existing clue, first select it from either \
clue list. \
\n\n\
<<bold::User preferences>> may be updated via the \
Preferences item on the Edit menu \
(or under the application menu item on Mac OS X). \
Preference changes take effect the next time Diagnil is started. \
\n\n\
A smaller group of settings may be changed using \
the Session Settings menu item. These changes take effect immediately \
and override the default values from Preferences. \
Changes may be made repeatedly within a session. The last settings \
will not be remembered or carried over into the next session. \
" ) ,

('View Menu Commands' ,
"Occasionally it helps to build up a small subarea of the puzzle \
in isolation and later overlay it onto the main grid. \
A set of <<bold::minigrids>> \
is provided for this purpose. Clicking the Swap Grids button \
(or selecting its equivalent from the View menu) switches to a view \
having four smaller grids that serve as scratch pads. You may use all \
the same commands to enter and place words on the minigrids \
as the main grid. A word may exist on only one grid at a time; \
placing a word will erase it from any other grid on which it lies. \
Words placed on a minigrid will be colored dark blue in the word lists \
and marked with '#' (instead of '+'). \
\n\n\
If you wish to change <<bold::working direction>> (from Across to Down or \
vice versa), select Toggle Word Entry Direction (Ctrl-Cmd-P). \
Moving the mouse cursor over either the Across or Down word panels \
will accomplish the same action, as will a (brief) click of the \
right mouse button on one of the grids. \
\n\n\
In clueful mode, Clues in Separate Window can help \
if the font size in the word list boxes is too small or if some characters \
are not rendered legibly. \
A .puz file often comes with a Notes section; its text is \
displayable in a separate window via Puzzle Notes/Hints. \
\n\n\
Sometimes it helps to view the grid pattern under construction \
without the clutter of words. The Grid Pattern menu item displays \
the black squares while omitting everything else. This feature also \
can be used after a solution has been completed to visualize the \
puzzle author's grid artwork. \
\n\n\
You can declare the size of your (clueless) puzzle using the \
Set Size and Symmetry \
option. Those squares beyond the size-bounded region will be displayed with \
a yellow background, although they are still usable. \
Turning on the <<bold::symmetry feature>> \
causes Diagnil to show, in a light gray shade, those black squares \
implied by grid symmetry. \
If you find these extra blocks misleading because of uncertainty about word \
location, you can turn off this feature and the clutter will disappear. \
See the section <<topic::Grid Symmetry>> for more information. \
\n\n\
Lists of recently performed actions can be displayed using the \
Undo/Redo List menu item. \
Diagnil emits warning and error messages as needed \
in response to user actions. \
The Recent Messages menu item allows you to revisit recent messages. \
" ) ,

('Grid Commands' ,
"Clicking the right mouse button over a grid toggles the working direction, \
that is, changes the direction for entering and manipulating words. \
If the button is held down, though, rather than being released immediately, \
a menu will pop up, giving you a choice of the following actions \
(assume that the mouse cursor lies over a cell at row R and \
column C in the grid). \
\n\n\
	<<bold::1. Renumber Word (Ctrl-Cmd-U)>> \
\n\n\
	Renumber the word starting in cell (R,C) \
using the adjustable word number cue displayed \
near or in its first cell. See topic <<topic::Word Number Aids>>. \
\n\n\
	<<bold::2. Move/Unpaste/Delete Across/Down Word>> \
\n\n\
	Choose these items to act on the word across or down containing \
cell (R,C). The Move action allows you to relocate a word by dragging it \
to a new site. The Unpaste action erases a word from the grid \
while retaining it in the word list panel. The Delete action \
removes the word completely. \
\n\n\
	<<bold::3. Move All/Adjacent/Connected Words>> \
\n\n\
	These options (and several that follow) allow you to move \
large sets of words on the grid. \
A two-step process is used. First, the desired words are collected \
based on the menu item chosen when the right button is released. \
Selected words are highlighted in red. \
Second, to move the selected words, \
simply <<bold::click left and drag the mouse cursor>> \
to the final destination cell. \
Transfer from one grid to another is also \
supported. If necessary, swap grid displays before selecting \
a destination cell with the second click. \
The first menu option (All Words) selects all \
words on the source grid. \
The second option (Adjacent Words) \
chooses those words adjoining cell (R,C) either directly or indirectly. \
The third option (Connected Words) \
chooses those words connected either directly or indirectly \
to cell (R,C) by crossing words (a subset of adjacent words). \
\n\n ",
('\t\t', 'connected-words.gif', '      Connected word selection') ,
u"\n\
	<<bold::4. Move Upper Left/Upper Right/Lower Left/Lower Right Region>> \
\n\n\
	These additional word-movement options allow you to select \
words based on rectangular regions of the grid. \
A two-step process is used. First, select a rectangular subgrid extending \
from cell (R,C) to one of the grid corners. A red box delineates this region. \
All words whose first letters are contained within the red box will be moved. \
Second, click left on the cell to which you want to move (R,C). All selected \
words will be shifted by the same distance. \
\n\n\
	<<bold::5. Move Left/Right Region Using Diagonal>> \
\n\n\
	These menu items invoke more complicated region-movement operations. \
They require you to supply a second point (R2,C2) \
on the grid using a second mouse click. \
(R,C) and (R2,C2) are used to create a three-segment boundary \
for splitting the grid into two regions. \
The boundary is formed by two vertical lines \
passing through (R,C) and (R2,C2) as well as the (diagonal) line \
between them. The destination (third) click determines how far to move \
the words (distance from R2,C2). \
A little experimentation is needed to grasp the mechanics. \
\n\n ",
('\t\t', 'diagonal-move.gif', '      Diagonal region boundary') ,
u"\n\
	<<bold::6. Move Selected Words Again>> \
\n\n\
	If the previous action moved a set of words using the commands \
above, the selected words can be moved again (without reselection) \
to a different location using this menu item. It also allows the \
word selection from an (immediately preceding) aborted action \
to be moved again. \
\n\n\
	<<bold::7. Wrap Rows around to Left>> \
\n\n\
	Imagine splitting the grid vertically just before column C. \
Now wrap around to the left all words placed at column C or higher, that is, \
move the right portion to the left and down one row. The existing \
left portion moves to the right by whatever amount is necessary. \
\n\n ",
('Before wrapping:  ', 'wrap-before.gif'),
('After wrapping:    ', 'wrap-after.gif') ,
u"\n\
	<<bold::8. Blacken/Whiten Squares(s)>> \
\n\n\
	Additional blocks (black squares) can be inserted by clicking \
on a cell, holding the button down, then dragging the mouse around \
to 'paint' the desired cells. Cells also can be whitened, \
except those serving as end blocks. \
\n\n\
	<<bold::9. Blacken/Whiten One Square (Ctrl-Cmd-W)>> \
\n\n\
	This action is similar to the one above except that a single cell \
is toggled from black to white or vice versa. \
A keyboard accelerator is provided for quick invocation. \
" ) ,

('Moving Words' ,
"All movement operations described under \
<<topic::Grid Commands>> can be <<bold::previewed>> \
by holding down the left mouse button and dragging \
the word(s) around the grid. \
The same is true of initial word placement in mouse-based navigation mode. \
Placement becomes fixed when the button is released. \
\n\n\
As words are being dragged, Diagnil checks whether there are any \
<<bold::conflicts>> that would result from \
placement at the mouse cursor's current location. \
Conflicts are possible between the end blocks of stationary words \
and the letters of words being moved, and vice versa. \
If any are detected, a red box is drawn around each conflicting cell. \
Letter clashes (two different letters in the same cell) \
are tolerated and will not be flagged by these checks. \
\n\n\
There are a few shortcut ways to move word groups besides the menu-based \
selections described in <<topic::Grid Commands>>. \
To initiate movement, <<bold::hold down the Shift key>> \
while left-clicking on a cell. Provided movement is within the same grid, \
the word group can be dragged to a new location. \
\n\n\
Three types of word movement shortcuts are provided. \
Clicking on a black square is equivalent to Move All Words. \
Clicking on the first letter of a word moves that one word only. \
If the letter starts both Across and Down words, however, \
then both words will be moved. \
Clicking on any other letter is equivalent to Move Adjacent Words. \
\n\n\
Note that the <<bold::Shift key may be released>> \
once the mouse button is clicked \
and held down. The Shift key needn't be held down while dragging. \
This helps when using a <<bold::touchpad>> on a laptop. \
" ) ,

('Word Number Aids' ,
"When entering words that are not being pasted (cursor lies over \
either word list panel), <<bold::default word numbers>> are available \
(displayed in blue above the entry boxes). In clueful mode, the \
corresponding clue item is also highlighted with a light pink \
background. Words typed without \
numbers acquire these defaults, after which they are increased by one \
(clueless mode) or advanced to the next valid number (clueful mode). \
They can be further incremented and decremented using \
<<bold::the + and - keys>>. \
\n\n\
Diagnil often can infer or guess what number a new word should take based \
on its first cell and surroundings on the grid. \
An optional feature to <<bold::estimate/infer word numbers>> \
can be enabled as a user preference. As a visual aid, \
the candidate number is displayed in red above or to the left of \
the applicable cell. In such cases, you can type \
the word without preceding it by a number or selecting its clue. \
First, pre-position \
the mouse or key cursor over a cell. Next, type the word and \
then press the Enter key. \
The word will be pasted at your chosen cell with the candidate number. \
\n\n\
Note that this estimation feature <<bold::does not reveal any information \
about the puzzle's solution>>. All inferences are based on the \
posted answers and their grid positions. \
The purpose of this feature is to save time and typing. \
The inferred numbers are meant to be ones that an experienced \
and engaged diagramless solver would be able to deduce easily \
during the course of working through a puzzle. \
\n\n\
Also note that crossing words and black squares are used to estimate \
candidate numbers. If these items are wrongly placed or \
black squares are missing, then Diagnil can guess incorrectly. \
The estimates can be adjusted using <<bold::the + and - keys>>. \
In early stages of puzzle solving, you might find \
the number suggestions unhelpful because word numbers cannot be \
narrowed sufficiently, let alone determined uniquely. \
As the structure takes shape, however, \
the suggestions will become more accurate. \
\n\n\
When words on the grid are \
out of order, distortion of the number cues is likely. \
No candidate number will be displayed if a cell cannot start a word. \
If no unused numbers are available, 'X' will be displayed, \
which is sometimes a hint that nearby words are misnumbered \
or misplaced. \
" ) ,

('Word Letter Aids' ,
"Words may be entered with <<bold::placeholder characters>> ('?') to indicate \
letters that have yet to be determined. When these letters are known, \
simply edit the word entry to replace the '?' characters. If a \
crossing word is pasted so that a letter and a '?' overlap, the '?' \
will be overwritten and the word automatically acquires the new letter. \
A word containing only '?' characters may be entered using notation \
such as '32 ? 6' (spaces optional), which will enter the word '??????'. \
\n\n\
If word N has not yet been entered, \
and N is the estimated word number for the cell under the cursor, \
then pressing Enter causes a new word \
to be formed from the contiguous letters found in the crossing direction. \
If word N already exists and is pasted on a grid, it will be refreshed \
by <<bold::acquiring crossing letters>>, thereby resolving its letter clashes \
in favor of the crossing words. The status line at the bottom of the \
application window shows what this revised word would be. \
\n\n\
You might find that crossing letters lack only a prefix or suffix needed \
to form a new word. Shortcut forms of word entry \
using the asterisk character as a <<bold::wild card>> are available. \
For example, you may type '*er' and click on a cell, \
which appends 'er' to a contiguous letter sequence such as 'paint' \
to form 'painter'. ('?' characters do not count as letters for this \
purpose, i.e., '?' will end a contiguous sequence.) \
This feature also \
can be used to extend an existing word in the same direction, \
for example, by typing '*s' to pluralize a word. \
More generally, several asterisks \
may be interspersed among letters to stitch together words from \
fragments on the grid. \
\n\n\
If the last letter entered abuts a sequence of crossing-word letters, \
they will turn red to indicate that they will be appended to \
the partial word when the Enter key is typed. \
This auto-completion feature makes it is unnecessary to type \
'*' to pick up the final letters. \
" ) ,

('Alternative Answers' ,
u"Often there are several plausible answers to a clue that \
come to mind. It can be helpful to enter them as alternatives \
so they can be recalled later. \
Diagnil allows you to type multiple words such as \
'horse,donkey,mule' instead of a single word. \
(They must be typed without intervening spaces.) The first \
word will become the current answer and the rest will become \
alternatives. The presence of alternatives is indicated by the \
suffix ',...' appended to answers in the word list panels: \
\n\n\
	32  - bears,... \N{black diamond} Four-legged honey fanciers \n\
\n\
To see the current list of alternative answers for a given word, \
right-click on its row in the word list panel. A menu of \
alternatives will be displayed along with their word lengths. \
If you select one of them by choosing its menu item, that \
alternative will swap places with the current answer. \
If none of the alternatives is selected, no changes will occur. \
Swapping of alternatives is an undoable action. \
\n\n\
A second way to create alternatives is invoked automatically every time \
an existing word is edited. When the revised word takes effect, the \
previous one is added to the alternatives list. This makes it easy to \
recall an earlier choice if you later realize it was correct after all. \
" ) ,

('Word Search' ,
"The search feature allows you to find answers that <<bold::match a pattern>> \
of letters. After invoking Find Word from the Edit menu \
(or typing Ctrl-Cmd-J), a small window will pop up. Type a sequence \
of letters, and all words from the Across or Down list containing \
those letters will be displayed. Selecting an item from \
the search-results list causes its contents to be transferred to \
a word entry panel, then hides the search window. From there you \
can proceed by editing or pasting on the grid. If the mouse cursor \
lies over a grid when Ctrl-Cmd-J is typed, letters starting \
at the mouse/key cursor location will be used to create a plausible \
search pattern. \
\n\n\
Besides letters and the placeholder character '?', patterns \
may contain 'wild-card' characters to specify matches more broadly. \
The character '.' matches an arbitrary letter while '*' matches \
a string of zero or more intervening letters. For example, 'b.ed' \
matches 'bred' while 'b*ed' matches 'bed', 'bred', 'baked' and 'basked'. \
\n\n ",
('\t\t', 'search.gif', '') ,
 ) ,

('Grid Symmetry' ,
u"Standard crosswords adhere to grid designs based on rotational symmetry. \
(This is the U.S. convention. Authors in other \
countries might follow different design rules.) \
What this means is that if a grid is rotated 180 degrees, \
the pattern of white and black squares will be identical. \
Most diagramless puzzles also follow this convention. \
For variety, though, as well as additional solving challenge, \
some diagramless puzzles use other types of symmetry. \
\n\n\
Awareness of grid symmetry helps in the solving process. \
For example, rotational symmetry helps \
you infer the word pattern on the lower right once enough of \
the upper left has been discovered. \
Diagnil offers an optional feature to help display the symmetrical nature \
of a grid while it is being constructed. \
Enabling this feature causes Diagnil to show, in a light gray shade, \
those black squares \
implied by grid symmetry. In other words, as each word is placed on \
the main grid, the end blocks of its symmetrical counterpart \
are displayed so you can better visualize the puzzle's structure. \
\n\n\
You may enable the symmetry feature under \
the View > Set Size and Symmetry menu item. \
You may also select symmetry attributes in the preference settings, \
which causes them to be applied by default when \
the Diagnil application is started. \
Diagnil supports the following symmetry types: \
\n\n\
	<<bold::\N{bullet} Rotational>> (standard symmetry) \n\
	<<bold::\N{bullet} Horizontal>> (left-to-right symmetry) \n\
	<<bold::\N{bullet} Vertical>> (top-to-bottom symmetry) \n\
	<<bold::\N{bullet} Diagonal, upper left to lower right>> (rows and columns interchanged) \n\
	<<bold::\N{bullet} Diagonal, upper right to lower left>> (rows and columns interchanged) \n\
\n ",
('Rotational:   ', 'rot-symm.gif') ,
('Horizontal:   ', 'horiz-symm.gif') ,
('Vertical:       ', 'vert-symm.gif') ,

u"For puzzles distributed electronically, the symmetry type \
is sometimes listed in the Notes section. \
In clueful mode Diagnil will extract this information \
from the Notes when present and will set the indicated symmetry type \
automatically. \
\n\n\
Changing the size and symmetry attributes can be applied to the current puzzle \
or to any new ones started in the same session. These attributes will be \
saved with the puzzle and will be restored when it is reopened later. \
" ) ,

('Completeness Criteria' ,
"Select First Square Hint to get the location of word 1-Across. \
Typically this hint is found in the Notes section, but this menu item \
will work even if the Notes are empty. \
\n\n\
In clueful mode, the puzzle's solution has been provided by the \
puzzle author for checking against your own. \
The features under menubar item \
Solution allow you to <<bold::check your words and their positions.>> \
Although seldom done anymore, some older puzzles had been distributed \
with their solutions in scrambled (locked) form. \
To unlock the solution for such a puzzle, you will need the four-digit \
key provided by the puzzle's distributor. \
\n\n\
To check a word against the solution, first select it \
in the word list panel, then invoke the Check Word menu item. \
Any incorrect letters in a word will be flagged. Position checking \
can be used when your words have been placed so the entire puzzle is \
tucked in the upper left corner of the grid. \
If you are thoroughly stuck and need some help, you can also reveal \
a word or its position. Positions are reported as a pair of numbers \
(R, C), where R is the row number of the word's first letter \
and C is its column number. Cell (1, 1) is the upper left corner. \
\n\n\
In clueless mode, you are on your own to a greater extent. \
Although there is <<bold::consistency checking>> performed on words and \
their placement, only minimal completeness checking can be carried out. \
You will have to decide whether the words are correct and when to stop \
building the puzzle. \
\n\n\
If desired, you may use the Finalize Puzzle command to perform \
additional checking of words and their placement on the grid. \
For example, if the letters of a word have been fully \
determined by crossing words, but the word has not yet been entered \
on a word list, you will be notified when you attempt to finalize \
the puzzle. \
You can enter such words by placing the mouse/key cursor \
on the first cell and pressing Enter. A sequence of contiguous letters \
in the chosen direction will be collected to form the new word for you. \
In some cases Diagnil will ask if you'd like to enter \
all the words automatically to complete the puzzle. \
\n\n\
In some unusual, nonstandard puzzle designs, there might be a few letters \
that are uncrossed, i.e., they only appear \
in one direction. Typically these are single letters \
in the middle of long phrases. \
Although the finalization check will flag them as missing words, \
it also asks if you would like to finalize \
the puzzle anyway. Click on OK if you think the puzzle is well-formed. \
Otherwise, you can cancel and add words as appropriate. \
" ) ,

('Preference Settings' ,
u"A few user-editable preference settings are available by selecting \
the Preferences item from the Edit menu. The following attributes \
can be changed. \
\n\n\
	\N{bullet} <<bold::Word number estimates>> \
are normally displayed on the grid \
as the mouse/key cursor moves. \
To improve deductive skills, beginners should consider \
disabling these word number inferences, then restoring them later. \
\n\n\
	\N{bullet} You may enable the \
<<bold::keyboard commands for navigating>> \
around grids, described in section <<topic::Grid Navigation>>. \
\n\n\
	\N{bullet} After every action in clueful mode, the puzzle is \
<<bold::automatically checked for completion.>> \
If any words are missing, but their correct letters appear due to \
crossing words, the puzzle is considered solved and will be finalized. \
Disable this checking if you prefer more explicit control. \
\n\n\
	\N{bullet} Answers in the word list panels can be displayed in either \
<<bold::lower or upper case>>. You can type them in either case, or a \
mixture of both, but they will be displayed uniformly according to \
this preference setting. \
\n\n\
	\N{bullet} If you have room on your display screen, you might find it \
helpful to use the <<bold::wide window layout>>, \
which places long word list panels on either side of the main grid. \
\n\n\
	\N{bullet} You can have Diagnil initially demarcate a \
<<bold::bounded region>> \
in the upper left corner of the main grid for building your puzzle. \
Cells beyond this region will be displayed with a \
yellow background, although they are still usable. \
\n\n\
	\N{bullet} The <<bold::symmetry feature>> \
can be enabled for a clueful puzzle or \
when a puzzle size has been declared. \
Several types of grid symmetry are selectable.  See the section \
<<topic::Grid Symmetry>> for a description. \
\n\n\
	\N{bullet} You can declare the <<bold::default size>> \
of your (clueless) puzzles \
by choosing one of several standard sizes or by setting the \
items Width (number of columns) and Height (number of rows). \
\n\n\
	\N{bullet} The <<bold::number of undoable steps>> \
to save can be adjusted. \
Beginners might want to increase this number if they find themselves \
backtracking a lot. \
\n\n\
	\N{bullet} Displaying the pop-up menu in response \
to a <<bold::right click>> occurs after a <<bold::short delay>>. \
Releasing the button within this period of time \
toggles the entry direction instead.  If the button is \
held down longer than the delay value, a menu will be popped up. \
The preset delay is 0.4 seconds. \
\n\n\
	\N{bullet} The <<bold::folder for storing puzzle files>> is \
user-selectable if you don't care to store puzzle files in the \
default location. The folder may be either a single name, \
which is considered relative to the base Diagnil folder, or a full \
absolute path name appropriate for the host platform, such as \
/home/joe/diag-puzzles or c:\\Users\joe\diag-puzzles. \
\n\n\
Besides these settings, Diagnil also saves the size and screen location \
of top level windows. If you resize or move them, your preferences \
will be remembered. \
" ) ,

('Crossword File Formats' ,
"In recent years, several new file formats have emerged from \
the puzzle community. \
Many think that the <<bold::Across Lite file format>>, \
which has been a <<bold::de facto standard>> for over a decade, \
should be replaced with a more modern and flexible standard. \
\n\n\
One format that might fill this role is the \
<<bold::Crossword Solver format>>, \
which has been gaining traction with crossword authors and publishers. \
It provides a wide array of features, including support for some \
non-crossword puzzle types. \
As of version 3.0, Diagnil can read Crossword Solver files \
and interpret the features most likely used in diagramless puzzles. \
\n\n\
While this format is considered open and unrestricted, \
some software developers have proposed other formats meant to be \
more explicitly decoupled from commercial products and their vendors. \
Two new file formats have been proposed as <<bold::open standards>>, \
intended to be freely available to all puzzle publishers and \
software developers. \
Diagnil now supports both of these as well. \
\n\n\
The first of the proposed open standards is called XPF, introduced \
in the summer of 2010. \
XPF offers more extensive crossword features than the Across Lite format, \
although most of these are unlikely to be used in diagramless puzzles. \
Diagnil was upgraded in version 2.2 to support this format. \
\n\n\
The second standard format is called ipuz, introduced in April 2011. \
It is actually a more encompassing standard than XPF because it \
allows the representation of many types of puzzles, not just crosswords. \
The crossword portion of the ipuz standard \
accommodates a large variety of features. \
Diagnil was upgraded in version 2.4 to support the relevant \
features of this format. \
\n\n\
One feature of the new formats, namely, \
the use of HTML-style text formatting such as \
bold or italic fonts, is not directly supported by Diagnil. \
Instead, an indication \
of the format is provided using punctuation characters. For example, \
a word in italics would appear as '<<word>>'. \
\n\n\
In general, Diagnil's support for these newer \
file formats is provisional. Only a subset of the puzzle features \
have been implemented. Those judged to be irrelevant to \
diagramless puzzles have been omitted. \
Further improvements will be made as new developments unfold in the area \
of file formats. \
\n\n\
You can open a Crossword Solver, XPF or ipuz file in Diagnil \
in the same manner as an Across Lite file. \
Instead of having file extension '.puz', Crossword Solver files will \
have file extension '.jpz', XPF files will have \
extension '.xpf' or '.xml' while ipuz files will have extension '.ipuz'. \
As with '.puz' files, once a '.jpz' or '.xpf' or '.ipuz' file has been \
opened and its contents imported, Diagnil will perform future Save \
actions by writing to a '.dg0' file. Thus, other than having a general \
awareness of the new file types, users will need to do nothing differently \
to make use of these enhancements. \
" ) ,

('Importing Scanned Clues' ,
"Another type of puzzle importing is available that \
doesn't import a complete puzzle file but rather imports only clues. \
The idea is to <<bold::capture clue lists>> \
that are available in <<bold::printed form>> \
by scanning them using an ordinary <<bold::flat-bed scanner>>, \
then processing the resulting images to extract the clues as plain text. The \
essence of diagramless puzzles, namely, that textual clues are all you need \
to define a puzzle, makes this approach possible. \
\n\n\
To take advantage of this feature, \
users will need a scanner and additional software to post-process \
the images captured by the scanner. An application \
that provides an Optical Character Recognition (OCR) function is required. \
(A digital image is simply a matrix of pixels; it needs to be interpreted \
to discern the correct sequence of letters and numbers.) \
Scanners typically are shipped with software having OCR \
capability. For example, OmniPage is a commonly bundled application that has \
OCR functions. If you already have such software, you will be ready to go. \
\n\n\
Note that despite providing \
reasonably high accuracy, OCR software often can't \
interpret an image perfectly. \
Extracted text still requires proofreading and editing. \
Diagnil will help you with this \
process and will try to compensate for distorted information. \
A little experimentation with all of the hardware and software \
components will be needed to arrive at a \
setup that works effectively. \
\n\n\
Once you have scanned and processed your puzzle clues using the OCR \
feature, you can either copy the clue lists to the clipboard or \
save them to a text file. Be sure to export the data in \
<<bold::plain text format>> (.txt file); \
don't use another file type such as PDF. \
To import the clues in Diagnil, use the menu item Import Clues \
under the File menu. Follow the instructions from that point on \
to complete the process. \
\n\n\
After successfully importing the clues, you can solve the puzzle as \
if it had come from an Across Lite file (.puz) or one of the other \
types (.jpz, .xpf, .ipuz). \
The main difference is that the clue-only form \
will lack the puzzle's solution \
along with a few items such as title, author, etc. \
Saving the puzzle will write out a file in Diagnil's file format (.dg0), \
which you will be able to work with in the usual ways. \
\n\n\
The effectiveness of this importing feature \
depends heavily on how well your OCR software recognizes \
text from printed material. \
One common problem is that the flow of text from one column to the next \
might not be properly recognized, causing the clue text to become \
jumbled. If this happens, your OCR software should have a way \
to indicate the column regions manually. \
For newspaper sources, it helps to clip out the relevant \
text from the page and scan it by itself so the OCR algorithm is not \
presented with extraneous image data. \
Certain OCR mistakes cannot be corrected automatically, \
such as missing quote characters, \
missing underscores, interchanging 'l' and '1', and extraneous marks \
interpreted as letters. Where feasible, Diagnil will highlight \
questionable clues for your attention. \
\n\n\
In any event, experimentation will be needed, first to see if this method \
works for you, and second to tune the steps to get the best results. \
You might find this feature more trouble than it's worth. Clearly, \
getting puzzles in a supported file format would be preferable. Until this \
becomes more common for diagramless puzzles, the clue-scanning feature \
can be used when the benefit outweighs the inconvenience. \
Loading puzzles onto a laptop before traveling is one such case, whereas \
desktop use can be done well enough by working from paper. \
\n\n\
One final admonition is warranted. Since crosswords are usually \
copyrighted by their publishers, exercise caution before posting \
any scanned puzzles online. \
Please don't use this feature to redistribute puzzles improperly. \
" ) ,

('Miscellaneous Notes' ,
u"<<heading1::Scrolling>> \
\n\n\
A crossword grid can be scrolled using the scroll bars \
along its bottom and right edges. In addition, mouse-wheel excursions \
can be used to achieve grid scrolling. \
When a grid is in Down-word entry \
mode, rotating the mouse wheel causes vertical scrolling. While in \
Across-word mode, horizontal scrolling is invoked. Holding down the \
shift key while rotating the mouse wheel causes scrolling \
perpendicular to these directions. \
\n\n\
<<heading1::Special Keys>> \
\n\n\
The Escape key, besides aborting multistep actions, also can serve \
to refresh the puzzle display and reset the software state. \
When a Shift key is pressed (with or without another key), \
temporary displays are removed, such as \
the warning messages overlaying the bottom of the grid and the suggested \
words that appear when moving to a new square. \
\n\n\
When editing word entries, several alternative \
<<bold::control-key bindings>> are available \
to facilitate the process. Ctrl+A positions the insertion cursor just \
before the first letter; Ctrl+E places the cursor after the last letter. \
Ctrl+F moves forward one character; Ctrl+B moves backward. Ctrl+K deletes \
all characters to the right of the cursor. Ctrl+T transposes two adjacent \
characters. These alternatives can be used in contexts where the arrow keys \
are reserved for grid cursor movement. \
\n\n\
<<heading1::Caveats>> \
\n\n\
You should be mindful of a few limitations in the current version. \
\n\n\
	\N{bullet} Support for the new, evolving puzzle-file formats \
(xpf, ipuz) is still provisional. \
If and when puzzles are distributed in these formats, \
further enhancements might be needed to keep up with these \
developing standards. \
\n\n\
	\N{bullet} Non-diagramless crosswords sometimes have special \
features such as circled letters, shaded squares and multiple letters \
per square. Special features aren't supported by Diagnil \
because they usually don't make sense in the diagramless case. \
If such a puzzle is opened, Diagnil might not be able to detect that it's \
different and the results could be unpredictable. \
\n\n\
	\N{bullet} The timer might appear to stop after \
a period of inactivity. \
Typing or moving the mouse will restart it and restore its display \
to the correct time. \
\n\n\
	\N{bullet} Entering answers having both wild card characters and \
alternative words (e.g., 'leo*d,puma,lion') is currently unsupported. \
The benefits of such a combination do not seem to be worth the \
extra complications that would arise. \
\n\n\
These items will be revisited in future versions of the software. \
" ) ,

('Getting Started' ,
"I suggest a brief practice session to familiarize yourself with \
Diagnil's features. Simply enter a few words into a new puzzle, \
place some words on the grid, then try making changes. A set of completed \
<<bold::sample grids>> is provided for illustration, \
available from the Help menu. \
Try opening one, then add, delete and move words around. First you \
will need to Undo the finalization step to 'unfreeze' the puzzle. \
(Don't select the sample called 'Practice-soln.dg0', which is the solution \
to the practice puzzle described below.) \
\n\n\
If you're completely new to diagramless puzzles, but are experienced \
with regular crosswords, you might try to solve one or \
two conventional puzzles (those having diagrams) using Diagnil. \
Take the clues from a (relatively easy) daily newspaper puzzle \
and solve it without looking at the grid. \
You can also open the 'puz' file for a standard crossword. \
This exercise will help you learn how \
the software works as well as the basic flow of diagramless solving. \
\n\n\
When you begin to work diagramless puzzles, remember that grid designs \
usually use rotational symmetry or, less commonly, \
one of the other symmetry types. Symmetry attributes help \
you infer the word pattern in one part of the puzzle once enough of \
another region has been discovered. \
This can be especially helpful if you're working a puzzle from \
the outside perimeter toward the middle. \
Examine the sample puzzles \
to see a variety of grid designs and get a sense of what to expect. \
\n\n\
A <<bold::practice puzzle>> is available when you're ready \
to use Diagnil in earnest. \
Select the Sample Grids menu item under Help \
and open the file <<bold::Practice.puz>>, which will allow you to solve \
in 'clueful' mode. \
This puzzle is rather small and easy to solve, allowing you to combine \
the mechanics of word entry and placement with the more \
strategic activity of deducing the overall layout. \
After successfully completing the practice puzzle, you should be \
ready to attempt serious diagramless puzzles from books, newspapers \
and online sources. \
\n\n\
Crossword purists might conclude that some software features, \
such as word search, word number inference, and symmetrical block display, \
provide too much help to the solver and \
therefore constitute 'cheating.' If you feel this way, simply restrict \
yourself to a conservative subset \
of the features once you've gained some familiarity \
with how the software works. \
" ) ,

('Placing Words', 
"Starting with just a list of word clues, there are various ways \
to approach the solving process. \
One is to work through the clue list to identify as many words as possible, \
entering them into the word list panels without trying to place them \
on the grid. After one pass through, you could begin pasting words \
on the grid. Alternatively, you might prefer to guess words and \
place them on the grid as soon as possible. Questionable words \
should be entered in the lists freely; they are easy to correct later. \
\n\n\
Progress requires placing the first few words. A few diagramless designs \
start with the first word in the upper left-hand corner, making it \
easy to begin. More commonly, though, diagramless puzzle designs \
<<bold::vary the location of the first word.>> \
Often this location is provided \
as a starting hint. Even if you don't know \
initially where the first word starts, or prefer not to use a hint, \
you can still place the word arbitrarily \
knowing you'll be able to make adjustments. I suggest starting with \
word 1 around column 5, which leaves some room to expand on the left. \
If you need more room, you can shift the whole puzzle right using \
the region movement commands described under topic <<topic::Grid Commands>>. \
Then you can start \
the second word about 5 spaces to the right of the first. Later you \
can shift left or right as needed to reach the desired layout. \
Placeholder characters (?) are helpful during the early stages \
to reserve cells for words before their letters are fully known. \
\n\n\
You might realize the second word doesn't belong on the first line, \
but instead goes on line 2 somewhere to the left of word 1. This can \
be fixed using the Wrap command. Feel free to place words \
speculatively -- you can always rearrange later. \
\n\n\
When faced with uncertainty, try inserting \
partial words or wild guesses. For example, \
if you know part of a word, you might choose to enter something like \
'64 water????', then place it on the grid to help fill out the region \
you're currently working. When the missing letters become known, simply \
edit the word to insert them. Often the missing letters will resolve \
themselves when crossing words are added. \
\n\n\
Diagramless puzzles typically have <<bold::large black areas>>, especially \
in the corners. Usually it's sufficient to blacken only the perimeters \
of these regions to make word boundaries apparent. This happens \
automatically as words are placed on the grid. The Finalize Puzzle \
command will supply the remaining black squares. \
With experience you should find it unnecessary to blacken any squares \
explicitly (using the grid commands on the pop-up menu). \
This feature is provided only for those who prefer to blacken interior \
areas as an aid to visualizing a puzzle's structure. \
" ) ,

('Using Minigrids' ,
"Although skillful solvers will seldom need them, minigrids \
are useful for working on small regions separately. One reason for \
doing this is when many words in an area are known, but their positions \
on the main grid cannot yet be determined. After fitting together a \
cluster of interlocking words, it merely needs to be moved to the \
main grid once its location is apparent. \
\n\n\
Another reason for minigrids is simply \
to try word guesses without disturbing the main grid. If they turn out \
to be wrong, placing the correct words on the main grid will \
delete the guesses from the minigrids automatically. \
\n\n\
When several consecutive Down words are known, but their positions \
within the puzzle are not, minigrids can be helpful. For example, \
if you know the words for 45, 46 and 47 Down, placing them next \
to each other on a minigrid allows you see \
fragments of several Across words. \
If no recognition is triggered by this, the search feature can help \
you find plausible candidates matching the fragments \
from among those existing on the word lists. \
" ) ,

('Additional Tips',
u"After you've successfully solved a few puzzles, adopting some or all of \
the following suggestions can help you solve more efficiently: \
\n\n\
	\N{bullet} Explicitly blackening squares is unnecessary. The \
end blocks placed automatically as words are entered should suffice \
for normal puzzle solving. \
\n\n\
	\N{bullet} If you missed the details in one of Diagnil's user messages, you can recall it using the Recent Messages item on the View menu. \
\n\n\
	\N{bullet} There is no great need for first-square hints. \
You can place \
1-Across anywhere on the top row, then move it (and any connected words) \
after you have a better idea of where it goes. \
\n\n\
	\N{bullet} Occasionally you'll find that you've \
placed words incorrectly \
and the changes you need to make are prevented by the interlocking \
structure you've created. \
Simply <<bold::unpaste>> one or more words (right-click on the grid) \
to decouple the linked words, then perform the necessary move(s). \
\n\n\
	\N{bullet} When word number inferences are wrong, \
it's easy not to notice, \
leading to answers attached to the wrong clues. These can be \
fixed by moving the mouse/key cursor over the first letter, raising or \
lowering the number with the + and - keys, then issuing \
Ctrl-Cmd-U to renumber the word. \
\n\n\
	\N{bullet} The + and - keys can be used to adjust word numbers \
in nearly all contexts where such numbers are involved. \
\n\n\
	\N{bullet} If you find that a sequence of letters \
from adjacent Across words is just \
what you need to form a not-yet-entered Down word (or vice versa), \
simply place the mouse/key cursor over the first letter and \
press Enter. \
You might first need to adjust the inferred word number using the +/- \
keys, or explicity type the correct number. \
\n\n\
	\N{bullet} If you've entered a guess in a word list panel \
but not yet pasted it on the grid, and you find \
that the crossing letters on the grid are now what you need instead, \
place the mouse/key cursor over the first letter (as in the previous tip) \
and press Enter. \
If Diagnil is suggesting your previous word guess instead \
(shown inside a green box), \
first type '*' (asterisk is the 'wild-card' character). It will match the \
crossing letters to form your desired word. \
\n\n\
	\N{bullet} In clueful mode, a puzzle will be completed automatically \
when all squares have acquired correct letters (unless this feature is \
disabled). That means some words need not be entered as long as their \
letters are provided by crossing words. \
\n\n\
	\N{bullet} After starting a new session, \
you may type Ctrl-Cmd-I to resume \
the puzzle you were last working on, or choose another recently opened \
puzzle using the Open Recent menu item. \
\n\n\
	\N{bullet} The timer that measures your solving time will \
pause automatically when you minimize the Diagnil window. \
\n\n\
Happy diagramless solving! \
" ) ,

)  # end of HelpItems


osx_comment = \
'\n\n\
For Mac OS X users: All keyboard accelerators based on \
Command-key combinations may also be invoked using an equivalent Control-key \
combination. For example, the Undo action may be invoked using either \
Command+Z or Ctrl+Z. \n'


