$(function() {
    $('#luci_homebase_add_existing').dialog({
        modal: true,
        title: 'Add Existing Cluster',
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
