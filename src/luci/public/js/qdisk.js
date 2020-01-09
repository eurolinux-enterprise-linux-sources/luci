var oldInput = null;

function remove_qdisk_heuristic(elem_id) {
    var existing_heuristics = $('.qdisk_heuristic')
    if ($(existing_heuristics).length == 1) {
        $('input:text', existing_heuristics).val("");
    } else {
        $(document.getElementById(elem_id)).remove();
    }
}

function add_qdisk_heuristic() {
    var parente = document.getElementById('qdisk_heuristics');
    if (!parente)
        return;

    var hnum = document.getElementById('num_heuristics');
    if (!hnum)
        return;

    var cur_hnum = Number(hnum.value) + 1;
    var existing_heuristics = $('.qdisk_heuristic').length;
    if (existing_heuristics >= 10) {
        alert('There is a maximum of 10 heuristics.');
        return;
    }

    var hstr = 'heuristic' + cur_hnum;
    var tr_id_str = 'qdisk_heuristic' + cur_hnum;

    var path_td = document.createElement('td');
    var path_input = document.createElement('input');
    path_input.setAttribute('name', hstr + ':hprog');
    path_input.setAttribute('id', hstr + ':hprog');
    path_input.setAttribute('type', 'text');
    path_input.setAttribute('class', 'text');
    path_td.appendChild(path_input);

    var interval_td = document.createElement('td');
    var interval_input = document.createElement('input');
    interval_input.size = 5;
    interval_input.setAttribute('name', hstr + ':hinterval');
    interval_input.setAttribute('id', hstr + ':hinterval');
    interval_input.setAttribute('type', 'text');
    interval_input.setAttribute('class', 'text');  
    interval_td.appendChild(interval_input);

    var score_td = document.createElement('td');
    var score_input = document.createElement('input');
    score_input.size = 5;
    score_input.setAttribute('name', hstr + ':hscore');
    score_input.setAttribute('id', hstr + ':hscore');
    score_input.setAttribute('type', 'input');
    score_input.setAttribute('class', 'text');
    score_td.appendChild(score_input);

    var tko_td = document.createElement('td');
    var tko_input = document.createElement('input');
    tko_input.size = 5;
    tko_input.setAttribute('name', hstr + ':htko');
    tko_input.setAttribute('id', hstr + ':htko');
    tko_input.setAttribute('type', 'input');
    tko_input.setAttribute('class', 'text');
    tko_td.appendChild(tko_input);

    var del_td = document.createElement('td');
    var del_img = document.createElement('img');
    del_img.setAttribute('src', '/images/delete-grey.png');
    del_img.setAttribute('onclick', 'remove_qdisk_heuristic("' + tr_id_str + '")');
    del_td.appendChild(del_img);

    var tr = document.createElement('tr');
    tr.setAttribute('id', tr_id_str);
    tr.setAttribute('class', 'qdisk_heuristic');
    tr.appendChild(path_td);
    tr.appendChild(interval_td);
    tr.appendChild(score_td);
    tr.appendChild(tko_td);
    tr.appendChild(del_td);
    parente.appendChild(tr);
    hnum.value = cur_hnum;
}

function disableChildrenInput(parent_name) {
    var parente = document.getElementById(parent_name);
    if (!parente)
        return;

    var inputElem = parente.getElementsByTagName('input');
    if (!inputElem || inputElem.length < 1) {
        oldInput = null;
        return;
    }

    if (inputElem[0].disabled)
        return;

    oldInput = new Array(inputElem.length);
    for (var i = 0 ; i < inputElem.length ; i++) {
        var e = inputElem[i];
        if (e.type == 'hidden')
            continue;

        e.disabled = true;
        if (e.type == 'button')
            continue;
        oldInput[e.name] = e.value;
        e.value = '';
    }
}

function enableChildrenInput(parent_name) {
    var parente = document.getElementById(parent_name);
    if (!parente)
        return;

    var inputElem = parente.getElementsByTagName('input');
    if (!inputElem || inputElem.length < 1 || !inputElem[0].disabled)
        return;

    for (var i = 0 ; i < inputElem.length ; i++) {
        var e = inputElem[i];
        e.disabled = false;
        if (e.type == 'button' || e.type == 'hidden')
            continue;
        if (oldInput && oldInput[e.name])
            e.value = oldInput[e.name];
        else
            e.value = '';
    }
    oldInput = null;
}

function reset_qdisk_vals(num_nodes) {
    var interval = $('#qdisk_interval');
    var votes = $('#qdisk_votes');
    var tko = $('#qdisk_tko');
    var min_score = $('#qdisk_min_score');

    if (interval) {
        $(interval).val('1');
    }

    if (votes) {
        $(votes).val('');
    }

    if (tko) {
        $(tko).val('');
    }

    if (min_score) {
        $(min_score).val('');
    }
}
