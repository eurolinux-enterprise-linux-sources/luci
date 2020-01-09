$(function() {
    $('#add_nodes_dialog').dialog({
        modal: true,
        title: 'Add Nodes to Cluster',
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
