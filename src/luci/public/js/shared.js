/*
 * Shared JS functions.
 *
 */

/**
 * Handle request for an overview collapse.
 */
function onOverviewCollapse() {
    var tb_shown = document.getElementById('toolbar_shown');
    var tb_collapsed = document.getElementById('toolbar_collapsed');
    var overview = document.getElementById('overview');

    if (tb_shown && tb_collapsed) {
        tb_shown.style.display = 'none';
        tb_collapsed.style.display = 'inherit';
        overview.style.display = 'none';
    }
}

/**
 * Handle request for an overview show.
 */
function onOverviewShow() {
    var tb_shown = document.getElementById('toolbar_shown');
    var tb_collapsed = document.getElementById('toolbar_collapsed');
    var overview = document.getElementById('overview');

    if (tb_shown && tb_collapsed) {
        tb_shown.style.display = 'inherit';
        tb_collapsed.style.display = 'none';
        overview.style.display = 'inherit';
    }
}

function allPasswdsSame(checkbox_obj) {
    if ($(checkbox_obj).is(':checked')) {
        var pw_elem = $('input:password', $(checkbox_obj.form));
        $.each(pw_elem, function() {
            var cur_val = $(this).val();
            if (cur_val) {
                $(pw_elem).val(cur_val);
                return false;
            }
        });
    }
}

function add_system_row(form) {
    var cur_count = $('.systemtriple', $(form)).length;
    var new_elem = $('#system_row_elem').clone();
    var input_elems = $(':input', $(new_elem));
    var num_nodes = Number(form.num_nodes.value) + 1;
    form.num_nodes.value = num_nodes;
    var new_id = $(form).attr('name') + '_system_row_elem' + num_nodes;
    $(new_elem).attr('id', new_id);
    $(input_elems).attr('name',
        function() { return this.name + num_nodes; });
    var img_elem = $('img', $(new_elem));
    $(img_elem).click(
	function() { $('#'+new_id).remove(); });
    $('.add_node_button_row', $(form)).before($(new_elem));
    if ($(form.allSameCheckBox).is(':checked')) {
        allPasswdsSame(form.allSameCheckBox);
    }
}

function update_node_hostname(form_elem) {
    var host_number = form_elem.name.substr(8);
    var rh_elem = $(':input[name="riccihost' + host_number + '"]', $(form_elem.form));
    if (!$(rh_elem).val()) {
        $(rh_elem).val(form_elem.value);
    }
}

function input_to_xml(elem) {
    var cur_xml_str = "";
    if ($(elem).attr('type') == 'checkbox') {
        if ($(elem).is(':checked')) {
            cur_xml_str += '<input name="' + $(elem).attr('name') + '" checked="checked" value="1" type="checkbox"/>';
        }
    } else {
        var cur_ival = $(elem).val();
        if (cur_ival) {
            cur_xml_str += '<input name="' + $(elem).attr('name') + '" value="' + Encoder.htmlEncode(cur_ival, true) + '" type="' + $(elem).attr('type') + '"/>';
        }
    }
    return cur_xml_str;
}

function update_multi_action(checkbox_obj) {
    if (!checkbox_obj || !checkbox_obj.form) {
        return;
    }
    var cur_form = $(checkbox_obj.form);
    var maction_buttons = $('.MultiAction', cur_form);
    var maction_items = $('.MultiActionItem', cur_form);

    if (checkbox_obj.checked !== false) {
        maction_buttons.removeAttr('disabled', 'disabled');
    } else {
        if ($(':checked', maction_items).length == 0) {
            maction_buttons.attr('disabled', 'disabled');
        }
    }
}

function reset_form(form_elem) {
    $(form_elem).each(function() {
        /* From jquery.form.js */
        if (typeof this.reset == 'function' || (typeof this.reset == 'object' && !this.reset.nodeType)) {
            this.reset();
        }

        $('select', this).each(function() {
            try {
                $(this).change();
            } catch (e) {}
        });
    });
}

function reset_service_form(form_elem) {
    reset_form(form_elem);
    try {
        $('#svc_root').empty();
    } catch (e) {}
}
