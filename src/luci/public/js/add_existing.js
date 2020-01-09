function add_existing_callback(data) {
    var add_existing_dialog_step1 = $("#add_existing_inner");
    var add_existing_dialog_step2 = $("#add_existing_dialog_final");

    if (data) {
        if ('errors' in data) {
            alert('Error adding this cluster: ' + data['errors'].join(' '));
            return;
        } else if (!'nodes' in data) {
            alert('Unable to retrieve the list of cluster nodes');
            return;
        }
        var tbody_elem = $("#sys_tbody");
        if (!tbody_elem) {
            return;
        }
        var num_nodes;
        var gen_string;
        for (num_nodes = 0 ; num_nodes < data['nodes'].length ; num_nodes++) {
            gen_string = '<tr>\n'
            gen_string += '<td><input class="text" name="node' + num_nodes + '_host" type="text" value="' + data['nodes'][num_nodes] + '" /></td>\n'
            gen_string += '<td><input class="text" name="node' + num_nodes + '_passwd" type="password" autocomplete="off" value="' + (data['nodes'][num_nodes] == $("#node0host").val() ? $("#node0passwd").val() : "") + '" /></td>\n'
            gen_string += '<td><input class="text" name="node' + num_nodes + '_riccihost" type="text" value="' + data['nodes'][num_nodes] + '" /></td>\n'
            gen_string += '<td><input class="text" name="node' + num_nodes + '_port" type="text" maxlength="5" size="5" value="11111" /></td>\n'
            gen_string += '</tr>'
            tbody_elem.append(gen_string);
        }
        $("#clustername").val(data['cluster']);
        $("#num_nodes").val(num_nodes);
        $("#cluster_name_span").append(data['cluster']);
    }
    add_existing_dialog_step1.replaceWith(add_existing_dialog_step2);
} 

function add_existing_async(form) {
    var errors = [];
    if (!form.hostname) {
        errors.append('No hostname was given');
    }
    if (!form.password) {
        errors.append('No password was given');
    }
    if (!form.port) {
        errors.append('No port was given');
    }
    $.post("/async/get_cluster_nodes",
        {
            'host': form.hostname.value,
            'port': form.port.value,
            'passwd': form.password.value
        }, add_existing_callback, 'json');
}
