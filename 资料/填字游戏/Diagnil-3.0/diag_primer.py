# Diagramless primer follows conventions for paragraphs in diag_help file.

primer_text = (
'''
<<italic::[ If you've solved diagramless puzzles before, you should have no need for this primer. Feel free to skip this and look instead at the Quick Start page or the full User's Guide. ]>>

<<heading1::Primer on Diagramless Solving>>

If you're an experienced solver of conventional crosswords, you might be curious about diagramless crosswords. You'd like to give them a try, but maybe you find the idea of diagramless solving a bit intimidating. Rest assured -- it's quite likely within your grasp. We'll help you get started.

Here's an observation that might put you at ease. To compensate for the extra challenge of discovering the grid layout, constructors aim for a clue and answer difficulty at the moderate level, usually around Tuesday or Wednesday on the New York Times scale. Those who can solve standard crosswords of medium to high difficulty should have no problem picking up diagramless solving.

You've probably never thought much about how words are numbered in crosswords, nor any of the other conventions of grid construction. Nevertheless, you've likely internalized these conventions without realizing it. Now we need to draw on that reservoir of subconscious knowledge because explicit awareness of the numbering scheme is important for diagramless solving.

Consider our practice puzzle, whose first few clues are the following:
<<bold::
		Across		Down
>>
	1	Breakfast food	1	Island for immigrants
	4	Demoted planet	2	Entrails
	6	Milk shake	3	Merged with Bell Atlantic
	7	Francophone capital	4	Peels
	8	Portal	5	Strange

Can we infer anything about the puzzle's structure from just the clue numbers? Surprisingly, we can. All puzzles begin with 1-Across, of course, but the number of the second Across word varies and its value is important. Because 1-Across runs along the top row, every one of its letters starts a Down word. Since these Down words are numbered consecutively, the number of the second Across word, 4 in this case, implies that 1-Across has three letters. This generalizes to a rule: you can always find the length of 1-Across.

''' ,
('\t\t', 'Length of 1-Across is known:      ', 'primer-1.gif') ,

'''Normally, this inference is the only one you can count on when you start solving. In some cases, though, there are other opportunities for deducing features of a diagram.

There are two noteworthy differences between diagramless grid designs and those of standard crosswords. First, diagramless grids can use other types of symmetry besides the standard rotational symmetry of regular crosswords. Grid symmetry is another one of those conventions you've probably not thought much about. Knowledge of the symmetry type can help during diagramless solving. A discussion of grid symmetry appears in the <<topic::User's Guide>>. In this primer, we assume standard rotational symmetry.

Second, diagramless grids often contain large areas of black squares, especially in the corners. This makes layouts less predictable, and sometimes allows the author to create a picture related to the puzzle's theme, adding a little spice to the solving experience.  See the <<topic::Sample Grids>> menu item for examples. The upshot of this trait is that 1-Across usually won't start in the first square; it can appear anywhere along the top row. Moreover, the distance to the second Across word is unknown. In fact, it needn't appear on the first row at all.

Now let's return to our example. We see clues for 4-Across and 6-Across. What might that tell us? Well, if 4-Across were to lie on the top row to the right of 1-Across, all of its letters would start Down words. Because the minimum length of a word is 3 (another one of those grid conventions), the third Across word would have to be numbered at least 7. But its number is 6, so we deduce that 4-Across can't lie on the first row -- it must go on the second.

OK, so it goes on row 2, but is there anything else about it we can infer? Indeed there is. If 4-Across were to lie completely to the left of 1-Across and not overlap any of the Down words 1-3, we would again need to have the third Across word numbered at least 7. This implies that 4-Across must overlap those 1/2/3-Down words somehow.

''' ,
('\t\t', 'Impossibility for 4-Across:     ', 'primer-2.gif') ,

'''Notice that there's a clue for 4-Down. This means the first letter of 4-Across also starts 4-Down and has a block (black square) above it. So 4-Across starts to the left of 1-Across but still overlaps 1/2/3-Down.

Have we now wrung out all the possible inferences? Not yet. Consider what would happen if 4-Across were to overlap 1-Down and 2-Down but not 3-Down. That would require a block where the second letter of 3-Down should go. Thus, we need to rule out that case (and similar ones), and conclude that 4-Across completely overlaps 1/2/3-Down.

''' ,
('\t\t', 'Another impossibility:        ', 'primer-3.gif') ,

'''Next we notice that 4-Across must have a letter for 5-Down, which cannot appear in the overlapping segment. We don't yet know whether it comes before or after the overlapping squares. What we do know is that 4-Across has length 5 and we've narrowed the possible word layouts to two cases:

''' ,
('\t\t', 'primer-4.gif', '      ', 'primer-5.gif') ,

'''The foregoing reasoning process is typical for diagramless solving, although you wouldn't carry it out this explicitly. After some practice, you'll be able to deduce little facts quickly as you work through a puzzle. Filling in words and reacting to any new constraints implied by the added information is a key part of solving. Integrating the spatial deductions with traditional knowledge-oriented crossword solving is what makes diagramless puzzles challenging and fun.

All right, let's fill in a few words to see how this might proceed. Diagramless constructors normally make 1-Across and its Down words fairly easy to help you get started. Let's guess that the answer to 1-Across is EGG and the answer to 3-Down is GTE. That gives us the following possibilities:

''' ,
('\t\t', 'primer-6.gif', '      ', 'primer-7.gif') ,

'''Now we have a crossing letter to constrain 4-Across. If we guess that the answer to 4-Across is PLUTO, we can narrow our possibilities to just one:

''' ,
('\t\t', '4-Across fully determined:     ', 'primer-8.gif') ,

'''At this point we don't yet know the correct starting square for 1-Across along the top row. We can place it arbitrarily and move everything later when the location has been determined. First-square hints often are provided by puzzle authors for those who want to use them.

The rest of the solving process alternates between guessing word answers and constructing the evolving diagram. To discover the layout, you make deductions about possible word locations as well as visually assess the full grid. These activities are mutually reinforcing and can be applied at different scales. Occasionally, for example, you can piece together a cluster of words in isolation without knowing where it fits on the main grid. Later on, when the overall structure of the grid becomes more apparent, you can see where the cluster belongs.

During the early and middle stages of the solving process, visual intuition plays a role. Sensing where words belong based on how the partial grid looks is one way that general crossword experience helps. During the later solving stages the grid layout will become fully known. At that point the solving process is reduced to that of a conventional crossword.

Alternating between answer guessing and grid deduction is the essence of diagramless solving. If you're good at guessing answers, the interlocking words you compile will allow you to make progress by pushing a "wavefront" of contiguous words outward. Eventually the overall shape of the grid will emerge. On the other hand, if you're good at making deductions from a variety of constraints, you can eliminate impossible cases and infer grid information even if you've discovered relatively few words. Obviously a combination of both skills would serve you well.

Not everyone will find this type of puzzle solving appealing. If, however, you're a crossword enthusiast who's receptive to new challenges, consider giving diagramless puzzles a chance. You might be surprised by how much you like them.
'''
)
