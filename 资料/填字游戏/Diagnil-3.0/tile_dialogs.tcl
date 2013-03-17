#
# Tile-based replacements for dialogs in tk_messageBox.
#

set diag_num 0

proc buttonTileDialog {butt} {
    global tile_dialog_button
    set tile_dialog_button $butt
}

proc centerTileDialog {win} {
    wm withdraw $win
    update idletasks
    set rw [winfo width .]
    set rh [winfo height .]
    set w  [winfo reqwidth $win]
    # add 30 pixels for window's title height:
    set h  [expr [winfo reqheight $win] + 30]
    set x  [expr [winfo rootx .] + ($rw - $w) / 2]
    set y  [expr [winfo rooty .] + ($rh - $h) / 2]
    wm geometry $win "+$x+$y"
    wm deiconify $win
}

proc postPredefinedDialog {type title message detail} {
    global diag_num tile_dialog_button
    set tile_dialog_button waiting
    set diag_win .tileDialog$diag_num
    incr diag_num
    ttk::dialog $diag_win -type $type \
        -command buttonTileDialog -parent . \
        -title $title -message $message -detail $detail
    centerTileDialog $diag_win
    vwait tile_dialog_button
    return $tile_dialog_button
}

proc postDisplayDialog {icon title message detail} {
    global diag_num tile_dialog_button
    set tile_dialog_button waiting
    set diag_win .tileDialog$diag_num
    incr diag_num
    ttk::dialog $diag_win -icon $icon \
        -command buttonTileDialog -parent . \
        -title $title -message $message -detail $detail \
        -buttons [list ok] -default ok
    centerTileDialog $diag_win
    vwait tile_dialog_button
    return $tile_dialog_button
}

proc tile_showinfo {title message} {
    return [postPredefinedDialog ok "Information" $title $message]
}

proc tile_showwarning {title message} {
    return [postDisplayDialog warning "User Notice" $title $message]
}

proc tile_showerror {title message} {
    return [postDisplayDialog error "Cannot Complete Action" $title $message]
}

proc tile_askokcancel {title message} {
    return [postPredefinedDialog okcancel "Confirm Action" $title $message]
}
