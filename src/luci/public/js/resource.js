$(function() {
    $('#add_resource_dialog').dialog({
        modal: true,
        title: 'Add Resource to Cluster',
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

function swap_resource_form(resource_form_id) {
    var form_jelem = $(document.getElementById(resource_form_id));
    $('#resource_form_area').empty();
    form_jelem.clone().appendTo('#resource_form_area');
}
