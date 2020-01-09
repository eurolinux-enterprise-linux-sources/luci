$(function() {
    var message_list = new Array();
    message_list['Delete'] = "Removing a cluster node from the cluster is a destructive operation that cannot be undone.";
    message_list['Reboot'] = "Reboot the selected nodes?";
    message_list['Leave Cluster'] = "Make the selected nodes leave the cluster?";

    $('#confirm_vanilla_dialog').dialog({
        modal: true,
        autoOpen: false,
        draggable: false,
        resizable: false,
        closeOnEscape: false,
        open: function(event, ui) { 
            $(this).parent().children().children('.ui-dialog-titlebar-close').hide();
        },
        buttons: {
            "Proceed": function() {
                $(this).dialog("close");
            },
            "Cancel": function() {
                $(this).dialog("close");
            }
        }
    });

    $(".confirm_link").click(function(e) {
        e.preventDefault();
        var targetUrl = $(this).attr("href");
        var trigger_elem_id = $(this).attr("id");
        var cur_action = null;

        if (trigger_elem_id == 'dh_delete')
            cur_action = 'Delete';
        else if (trigger_elem_id == 'dh_reboot')
            cur_action = 'Reboot';
        else if (trigger_elem_id == 'dh_leave')
            cur_action = 'Leave Cluster';
        else
            return true;

        $("#confirm_vanilla_dialog").dialog({
            open: function(event, ui) { 
                $(this).parent().children().children('.ui-dialog-titlebar-close').hide();
            },
            closeOnEscape: false,
            buttons: {
                "Proceed": function() {
                    window.location.href = targetUrl;
                    $(this).dialog("close");
                },
                "Cancel" : function() {
                    $(this).dialog("close");
                }
            }
        });
        try {
          $('#vanilla_confirm_span').empty();
          $('#vanilla_confirm_span').append(message_list[cur_action]);
        } catch (e) {}
        $("#confirm_vanilla_dialog").dialog("open");
    });

    $("[type=submit],[type=image]").bind("click", function(e) {
        $(this).attr("trigger_elem", "True");
    });

    $(".confirm_form").submit(function(e) {
        var cur_form = this;
        var cur_action = null;

        var trigger_elem = $("[trigger_elem=True]").get(0);
        if (trigger_elem.id == 'tb_delete')
            cur_action = 'Delete';
        else if (trigger_elem.id == 'tb_reboot')
            cur_action = 'Reboot';
        else if (trigger_elem.id == 'tb_leave')
            cur_action = 'Leave Cluster';
        else
            return true;
        trigger_elem.removeAttribute('trigger_elem');
        e.preventDefault();
        var ret = $("#confirm_vanilla_dialog").dialog({
            closeOnEscape: false,
            open: function(event, ui) { 
                $(this).parent().children().children('.ui-dialog-titlebar-close').hide();
            },
            buttons: {
                "Proceed": function() {
                    $(this).dialog("close");
                    $(cur_form).append('<input type="hidden" name="MultiAction" value="' + cur_action  + '"/>');
                    cur_form.submit();
                    return true;
                },
                "Cancel" : function() {
                    $(this).dialog("close");
                    return false;
                }
            }
        });
        try {
          $('#vanilla_confirm_span').empty();
          $('#vanilla_confirm_span').append(message_list[cur_action]);
        } catch (e) {}
        $("#confirm_vanilla_dialog").dialog("open");

    });
});

function add_fenceinst(parent_id, fence_type, fence_device) {
    var form_jelem = $(document.getElementById(parent_id));
    if (!form_jelem) {
        return;
    }
    var num_inst = 1;
    if (!fence_type) {
        if (fence_device == "-1") {
            $(form_jelem).empty();
        }
        return;
    }
    var inst_form_jelem = $(document.getElementById(fence_type + '_instance')).clone();
    if (!inst_form_jelem) {
        return;
    }

    var fenceinst_id = parent_id;
    $(inst_form_jelem).attr('id', fenceinst_id);
    $(inst_form_jelem).attr('class', 'fenceinst');

    var parent_dev = $('input[name="parent_fencedev"]', inst_form_jelem);
    $(parent_dev).val(fence_device);

    $('input[name="remove_fence"]', inst_form_jelem).remove();
    $(form_jelem).replaceWith($(inst_form_jelem));
}

function gen_fence_xml(form) {
    var fence_div_jelem = [ '#primary_fence_dev', '#secondary_fence_dev' ];
    var fence_xml_field = [ form.level1_xml, form.level2_xml ];

    for (var i = 0 ; i < fence_div_jelem.length ; i++) {
        var level_xml_str = "";
        var device_jelem = $(fence_div_jelem[i]).find('.fencedev');

        /* Iterate over each device in each level */
        for (var fd = 0 ; fd < $(device_jelem).length ; fd++) {
            var cur_fd = $(device_jelem).eq(fd);
            var device_form = $(cur_fd).find('.fencedevform');
            var cur_fence_id = $(cur_fd).attr('id');
            var fence_dev_input = $(':input', device_form);
            var cur_xml_str = '<form id="' + cur_fence_id + '">';
            $(fence_dev_input).each(function(idx) {
                cur_xml_str += input_to_xml(this);
            });
            cur_xml_str += '</form>'
            level_xml_str += cur_xml_str;

            /* Iterate over each instance of the current device */
            var inst_jelem = $(cur_fd).find('.fenceinst');
            for (var fi = 0 ; fi < $(inst_jelem).length ; fi++) {
                var cur_fi = $(inst_jelem).eq(fi);
                var cur_fi_id = $(cur_fi).attr('id');
                var fence_inst_input = $(':input', cur_fi)
                var inst_xml_str = '<form id="' + cur_fi_id + '">';
                $(fence_inst_input).each(function(idx) {
                    inst_xml_str += input_to_xml(this);
                });
                inst_xml_str += '</form>'
                level_xml_str += inst_xml_str;
            }
        }

        fence_xml_field[i].value = '<formlist>' + level_xml_str + '</formlist>';
    }
    form.submit();
}

function fence_method_remove(fence_form_id, method_name) {
    var form_elem = document.getElementById(fence_form_id);
    if (form_elem && method_name) {
        $(form_elem.method_to_remove).attr('value', method_name);
        form_elem.submit();
    }
    return false;
}

function fence_method_moveup(fence_form_id, method_name) {
    var form_elem = document.getElementById(fence_form_id);
    if (form_elem && method_name) {
        $(form_elem.moveup_method).attr('value', method_name);
        form_elem.submit();
    }
    return false;
}

function fence_method_movedown(fence_form_id, method_name) {
    var form_elem = document.getElementById(fence_form_id);
    if (form_elem && method_name) {
        $(form_elem.movedown_method).attr('value', method_name);
        form_elem.submit();
    }
    return false;
}

function fence_instance_remove(fence_form_id, method_name, instance_name) {
    var form_elem = document.getElementById(fence_form_id);
    if (form_elem && method_name && instance_name) {
        $(form_elem.fenceinst_to_remove_method).attr('value', method_name);
        $(form_elem.fenceinst_to_remove).attr('value', instance_name);
        form_elem.submit();
    }
    return false;
}
