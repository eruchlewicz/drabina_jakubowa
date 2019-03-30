$(document).ready(function () {

    var total_hours = $('#batch_hours');
    var begin_batch = $('#id_begin_batch');
    var begin_date = $('#id_begin_date');
    var end_date = $('#id_end_date');

    // date
    function split_date (date) {
        var date_val = date.val();
        var split = date.val().split(' ');
        var dates = split[0].split('.');
        date_val = dates[2]+"-"+dates[1]+"-"+dates[0];
        return date_val;
    }

    var beg_date_val = split_date(begin_date);
    var end_date_val = split_date(end_date);
    var begin_batch_val = split_date(begin_batch);
    var diff_begin = Math.abs(Math.ceil((new Date(begin_batch_val) - (new Date(beg_date_val))) / 1000 / 60 / 60 / 24));
    var diff = Math.abs(Math.ceil((new Date(beg_date_val) - (new Date(end_date_val))) / 1000 / 60 / 60 / 24));

    console.log("1");

    if(diff_begin === 0) total_hours.text((diff-3)*14);
    else if(diff_begin === 1) total_hours.text((diff-2)*14);
    else total_hours.text((diff-1)*14);
});