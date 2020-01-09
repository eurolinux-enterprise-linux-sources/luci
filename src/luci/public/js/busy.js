var busy_interval = null;
var pending_request = false;
var ui_blocked = false;
var refresh_window = false;
var force_redirect = null;
var cur_errors = 0;

function get_task_status(cluster_name) {
    if (pending_request == true) {
        return;
    }
    $.ajax({
        type: 'POST',
        url: '/async/is_cluster_busy',
        cache: false,
        data: 'cluster=' + cluster_name,
        dataType: 'json',
        error: function(jqXHR, textStatus, errorThrown) {
            pending_request = false;
        },
        success: function(busy_obj) {
            pending_request = false;

            var busy = busy_obj['code'];

            $('#status_msg_details').empty();

            if (busy != 1) {
                $.unblockUI();
                ui_blocked = false;
                if (!('data' in busy_obj)) {
                    clearInterval(busy_interval);
                    busy_interval = null;
                    return;
                }
            }

            var install_subtasks = [
                '',
                'installing packages',
                'disabling cluster services',
                'rebooting node',
                'setting cluster configuration',
                'enabling cluster services',
                'joining cluster'
            ];

            for (var cur_key in busy_obj['data']) {
                var cur = busy_obj['data'][cur_key];
                var substatus = '';

                try {
                    if (cur.db_task_type == 1 || cur.db_task_type == 3) {
                        if ('module_offset' in cur) {
                            var cur_offset = cur.module_offset;
                            if (cur_offset < install_subtasks.length) {
                                substatus = ': ' + install_subtasks[cur_offset];
                            }
                        }
                    }
                } catch (e) {}

                if (cur.ricci_code == 0) {
                    if ('done' in cur) {
                        if (cur.db_task_type != 2 && cur.db_task_type != 9) {
                            // 2=set conf, 9=activate conf
                            try {
                                $.jnotify(cur.db_status + ' completed successfully', true);
                            } catch (e) {}
                        }
                        if (cur.db_task_type == 1 || cur.db_task_type == 3 ||
                            cur.db_task_type == 4 || cur.db_task_type == 104)
                        {
                            // create cluster=1, create node=3,
                            // delete node=4, 104
                            refresh_window = true;
                        } else if (cur.db_task_type == 8) {
                            // cluster delete
                            force_redirect = '/cluster/';
                        }
                    } else {
                        // submodule for create node finished, but the job
                        // is still pending
                        if (cur.db_task_type == 1 || cur.db_task_type == 3) {
                            $('<li class="status_msg_text">Creating cluster node ' + cur.host + substatus + '</li>').appendTo($('#status_msg_details'));
                        } else if (cur.db_task_type == 4 || cur.db_task_type == 8 || cur.db_task_type == 104) {
                            $('<li class="status_msg_text">Deleting cluster node ' + cur.host + substatus + '</li>').appendTo($('#status_msg_details'));
                        } else {
                            $('<li class="status_msg_text">' + cur.db_status + substatus + '</li>').appendTo($('#status_msg_details'));
                        }
                    }
                } else if (cur.ricci_code == 1 || cur.ricci_code == -102) {
                    // module is executing or queued
                    $('<li class="status_msg_text">' + cur.db_status + substatus + '</li>').appendTo($('#status_msg_details'));
                } else if (cur.ricci_code == -1) {
                    try {
                        $.jnotify(cur.db_status + " failed: " + cur.ricci_msg, "error", true);
                        cur_errors++;
                    } catch (e) {}
                } else {
                    /* unknown status */;
                    $('<li class="status_msg_text">' + cur.status + substatus + '</li>').appendTo($('#status_msg_details'));
                }
            }

            if (busy == 1) {
                if (!ui_blocked) {
                    $.blockUI({ message: $('#status_msg_area') });
                    ui_blocked = true;
                }
            } else {
                if (cur_errors < 1) {
                    if (refresh_window == true) {
                        window.location.reload();
                    } else if (!busy && force_redirect != null) {
                        window.location = force_redirect;
                    }
                }
            }
        }
    });
    pending_request = true;
}

function poll_cluster_busy(cluster_name) {
    busy_interval = setInterval(function(){get_task_status(cluster_name);}, 2000);
}
