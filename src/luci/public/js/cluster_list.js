$(function() {
    $('#add_existing_dialog').dialog({
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

$(function() {
    $('#create_cluster_dialog').dialog({
        modal: true,
        title: 'Create New Cluster',
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
