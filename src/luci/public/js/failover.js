/*
 * JS functions for Failover domains.
 *
 */

/**
 * On page load, disable the priority settings for the nodes that are not
 * members of the current failover domain.
 */
function onLoad() {
    var input_elems = document.getElementsByTagName("input");
    for (var i = input_elems.length - 1 ; i >= 0 ; i--) {
        var input_elem = input_elems[i];

        if (input_elem.className == "input_priority_disabled") {
            input_elem.disabled = true;
            input_elem.className = "input_priority";
        }
    }
}

/**
 * On 'member' checkbox change, enable/disable the priority settings
 * for the node and change the style appropriately.
 *
 * @param elem_id Identifier of the checkbox being changed.
 */
function onCheckMember(elem_id) {
    if ($('#ordered').is(':checked')) {
        var elem = document.getElementById(elem_id.replace(".check", ".priority"));
        if (elem) {
            elem.disabled = elem.disabled ^ 1;
        }
    }
}

function updateNodePriorityState(checkbox) {
    if (!$(checkbox).is(':checked')) {
        $(".input_priority").attr('disabled', 'disabled');
    } else {
        $(".input_priority").each(function(i) {
            var cb_elem = document.getElementById($(this).attr('id').replace('.priority', '.check'));
            if ($(cb_elem).is(':checked')) {
                $(this).removeAttr('disabled');
            }
        });
    }
}
