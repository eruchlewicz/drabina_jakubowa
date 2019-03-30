$(document).ready(function () {
    var begin = $('#id_begin_date');
    var end = $('#id_end_date');
    var rooms = $('#id_room');
    var empty_rooms = $('#empty_rooms');
    var begin_date = 0;
    var end_date = 0;

    function split_beg_date () {
        var beg_date_val = begin_date.val();
        var split = begin_date.val().split(' ');
        var date = split[0].split('.');
        beg_date_val = date[2]+"-"+date[1]+"-"+date[0];
        return beg_date_val;
    }

    function split_end_date () {
        var end_date_val = end_date.val();
        var split2 = end_date.val().split(' ');
        var date2 = split2[0].split('.');
        end_date_val = date2[2]+"-"+date2[1]+"-"+date2[0];
        return end_date_val;
    }

    $('#id_begin_date').change(function () {
        begin_date = new Date(split_beg_date());
        end_date = new Date(split_end_date());
        console.log(begin_date);
        $('#empty_rooms').append('<span>{{ '+begin_date+'|empty_rooms:\"'+end_date+'\" }}</span>');
    });

    $('#id_end_date').change(function () {
        begin_date = new Date(split_beg_date());
        end_date = new Date(split_end_date());
        console.log(begin_date);
        $('#empty_rooms').append('<span>{{ '+begin_date+'|empty_rooms:\"'+end_date+'\" }}</span>');
    });

});