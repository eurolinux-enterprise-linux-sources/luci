$(function() {
    $('#add_user_dialog').dialog({
        modal: true,
        title: 'Add a User',
        width: '720px',
        autoOpen: false,
        draggable: false,
        resizable: true,
        closeOnEscape: false,
        open: function(event, ui) {
            $(this).parent().children().children('.ui-dialog-titlebar-close').hide();
        },
    });
})
