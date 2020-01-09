function update_user_mode(cb_obj) {
    if ($(cb_obj).is(':checked')) {
        $.cookie("expertMode", 1, {expires: 7});
    } else {
        $.cookie("expertMode", 0, {expires: 7});
    }
}
