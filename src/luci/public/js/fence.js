$(function() {
    $('#create_fencedev_dialog').dialog({
        modal: true,
        title: 'Add Fence Device (Instance)',
        width: '520px',
        autoOpen: false,
        draggable: false,
        resizable: true,
        closeOnEscape: false,
        open: function(event, ui) { 
            $(this).parent().children().children('.ui-dialog-titlebar-close').hide();
        }, 
    });

    $('#create_fencemethod_dialog').dialog({
        modal: true,
        title: 'Add Fence Method to Node',
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

function swap_fence_form(fence_form_id, container_id) {
    var form_jelem = $(document.getElementById(fence_form_id));
    var cont_jelem = $(document.getElementById(container_id));
    cont_jelem.empty();
    form_jelem.clone().appendTo(cont_jelem);
}
