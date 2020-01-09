$(function() {
    $('#create_fdom_dialog').dialog({
        modal: true,
        title: 'Add Failover Domain to Cluster',
        width: '520px',
        autoOpen: false,
        draggable: false,
        resizable: true,
        closeOnEscape: false,
        open: function(event, ui) { 
            $(this).parent().children().children('.ui-dialog-titlebar-close').hide();
        }, 
    });
})
