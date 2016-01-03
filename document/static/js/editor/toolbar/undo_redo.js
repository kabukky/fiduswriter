// toolbar undo / redo

jQuery(document).on('mousedown', '#button-undo:not(.disabled)', function (event) {
    theEditor.editor.execCommand("undo");
});

jQuery(document).on('mousedown', '#button-redo:not(.disabled)', function (event) {
    theEditor.editor.execCommand("redo");
});