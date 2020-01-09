$(function() {
    $('#confirm_remove_service_dialog').dialog({
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

        $("#confirm_remove_service_dialog").dialog({
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
        $("#confirm_remove_service_dialog").dialog("open");
    });

    $("[type=submit],[type=image]").bind("click", function(e) {
        $(this).attr("trigger_elem", "True");
    });

    $(".confirm_form").submit(function(e) {
        var cur_form = this;

        var trigger_elem = $("[trigger_elem=True]").get(0);
        if (trigger_elem.id != 'tb_delete') {
            return true;
        }
        
        e.preventDefault();
        var ret = $("#confirm_remove_service_dialog").dialog({
            closeOnEscape: false,
            open: function(event, ui) { 
                $(this).parent().children().children('.ui-dialog-titlebar-close').hide();
            },
            buttons: {
                "Proceed": function() {
                    $(this).dialog("close");
                    $(cur_form).append('<input type="hidden" name="MultiAction" value="Delete"/>');
                    cur_form.submit();
                    return true;
                },
                "Cancel" : function() {
                    $(this).dialog("close");
                    return false;
                }
            }
        });
        $("#confirm_remove_service_dialog").dialog("open");
    });
});

$(function() {
    $('#add_service_dialog').dialog({
        modal: true,
        title: 'Add Service Group to Cluster',
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
    $('#insert_resource_dialog').dialog({
        modal: true,
        title: 'Add Resource to Service',
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

function insert_resource_dialog(form, dest_id, parent_id) {
    var res_selector = document.getElementById('resource_selector');
    res_selector.onchange = function() {
        insert_resource(this.options[this.selectedIndex].value, dest_id, form, parent_id);
        this.selectedIndex = 0;
        $('#insert_resource_dialog').dialog('close');
    };
    $('#insert_resource_dialog').dialog('open');
}

function insert_resource(res_id, container_id, form, parent_id) {
    var num_res = Number(form.res_count.value);
    var is_vm = false;

    if (res_id == 'vm_resource') {
        is_vm = true;
        if ($('.reslevel').length != 0) {
            alert("VMs may have no children and may not be children of other resources.");
            return;
        }
        var sel_elem = $('.resource_selector', form);
        $(sel_elem).remove();
    }
    var is_global = res_id.match(/^global_res_/) != null;

    form.res_count.value = num_res + 1;

    var cur_id_str = 'res_' + num_res;
    var td_id_str = 'td_' + cur_id_str;
    var table_id_str = 'table_' + cur_id_str;
    var res_anchor_name = 'anchor_' + cur_id_str;

    var svc_tables = $('<a name="' + res_anchor_name + '" id="' + res_anchor_name + '"/><table class="detailstable" id="' + table_id_str + '"><thead class="svc_padding"><tr class="svc_padding"><th class="svc_padding" width="5"/><th class="svc_padding" width="98%"/><th class="svc_padding" colspan="3"/></tr></thead><tbody><tr class="svc_res_table"><td></td><td align="right" class="svc_padding" colspan="4"><a href="#" onclick="$(\'#' + table_id_str + '\').remove();return false;">Remove</a></td></tr><tr><td class="svc_padding"></td><td colspan="4" class="svc_content" id="' + td_id_str + '"></td></tr></tbody></table>');
    var containing_div = $('<div class="reslevel"></div>');
    $(containing_div).attr('id', cur_id_str);

    var child_div = $('<div class="reschild"></div>');
    $(child_div).attr('id', 'children_res_' + num_res);

    var cntrl_div = $('<div class="row rescntrl"></div>');
    if (!is_vm) {
        var cntrl_button = $('<input type="button" class="button small silver" value="Add Child Resource" onclick="insert_resource_dialog(form, \'children_res_' + num_res + '\', \'' + cur_id_str + '\');"></input>');
        $(cntrl_button).appendTo($(cntrl_div));
    }

    var dest_jelem = $('\'#' + container_id + '\'', form);
    if (!dest_jelem) {
        return;
    }

    var form_jelem = $(document.getElementById(res_id)).clone();
    if (!form_jelem) {
        return;
    }
    $(form_jelem).removeAttr('id');

    if (is_global) {
        $('<input type="hidden" name="global" value="1"/>').appendTo($(form_jelem));
        $(':input', form_jelem).attr('disabled', 'disabled');
        $('.subtree', form_jelem).removeAttr('disabled', 'disabled');
    }

    var cur_resid_elem = $('input[name="form_id"]', form_jelem);
    $(cur_resid_elem).val(cur_id_str);

    var parent_resid_elem = $('input[name="parent_id"]', form_jelem);
    $(parent_resid_elem).val(parent_id);

    var tree_level_elem = $('input[name="tree_level"]', form_jelem);
    $(tree_level_elem).val(0);

    $(form_jelem).appendTo($(containing_div));
    $(cntrl_div).appendTo($(containing_div));
    $(child_div).appendTo($(containing_div));
    $(svc_tables).appendTo($(dest_jelem));
    $(containing_div).appendTo($(document.getElementById(td_id_str)));
    window.location.href = '#' + res_anchor_name;
}

function submit_svc_form(form) {
    var resform_jelem = $(form).find('.rescfg');
    var xml_str = '<formlist>';

    for (var i = 0 ; i < $(resform_jelem).length ; i++) {
        var cur_res = $(resform_jelem).eq(i);
        var cur_res_input = $(':input', cur_res);
        var cur_id = $('input[name="form_id"]', cur_res);
        var parent_id = $('input[name="parent_id"]', cur_res);
        var cur_xml = '<form id="' + $(cur_id).val() + '" parent="' + $(parent_id).val() + '">';
        $(cur_res_input).each(function(idx) {
            cur_xml += input_to_xml(this);
        });
        cur_xml += '</form>';
        xml_str += cur_xml;
    }
    form.form_xml.value = xml_str + '</formlist>';
    form.submit();
}

function update_restart_opts(recovery_policy) {
    opt_elems = $('.restart_opt')
    if (recovery_policy != 'restart' && recovery_policy != 'restart-disable') {
        $(opt_elems).attr('disabled', 'disabled');
    } else {
        $(opt_elems).removeAttr('disabled', 'disabled');
    }
}

function move_service_group(baseurl) {
    var move_action = $('#move_action').val();
    var preferred_node = $('#preferred_node').val();

    location.href = baseurl + '&preferred_node=' + preferred_node + '&move_action=' + move_action;
}
