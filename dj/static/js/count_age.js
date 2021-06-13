$(document).ready(function () {
    var age = $('#age').text();
    var begin = new Date($('#begin_date').text());
    var end = new Date($('#end_date').text());

    var year = age.slice(0,2);
    var month = parseInt(age.slice(2,4));
    if(month>12) {
        month -= 20;
        month = "0" + month;
        year = "20" + year;
    }
    else {
        if(month<10) month = "0" + month;
        year = "19" + year;
    }
    var day = age.slice(4,6);
    var full_date_string = year + "-" + month + "-" + day;
    var this_year_bday_string = begin.getFullYear() + "-" + month + "-" + day;
    var full_date = new Date(full_date_string);
    var this_year_bday = new Date(this_year_bday_string);

    function calculateAge (bday) {
        var ageDifMs = Date.now() - bday.getTime();
        var ageDate = new Date(ageDifMs);
        return Math.abs(ageDate.getUTCFullYear() - 1970);
    }

    function check_if_has_birthday (bday) {
        return begin.getTime() <= bday.getTime() && bday.getTime() <= (end.getTime()+ (3600000 * 24))
    }

    var counted_age = calculateAge(full_date);
    var age_label = "lat";
    var last_char = parseInt(String(counted_age).slice(-1));

    if(counted_age === 1) age_label = "rok";
    else if($.inArray(last_char, [2, 3, 4]) !== -1 && counted_age !== 12 && counted_age !== 13 && counted_age !== 14)
        age_label = "lata";

    check_if_has_birthday(this_year_bday);

    $('#age').text(counted_age + " " + age_label + " (" + full_date_string + ")");
    $('#age').show();
    if(check_if_has_birthday(this_year_bday)) $('#age').append('<span class="bold red"> - urodziny </span></span><i class="fa fa-birthday-cake blue"></i>');
});