$(document).ready(function () {

    var begin = new Date($('#begin_date').text());
    var end = new Date($('#end_date').text());

    var this_year_bday_string = "";
    var full_date = 0;
    var this_year_bday = 0;

    $(".if_bd").each(function( index ) {
        var pesel = $( this ).text();

        initialize(pesel);

        var birthday = check_if_has_birthday(this_year_bday);
        if(birthday) {
            $( this ).parent().children(".bd_cake").append('<i class="fa fa-birthday-cake blue"></i>');
        }
    });

    function initialize (age) {
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
        this_year_bday_string = begin.getFullYear() + "-" + month + "-" + day;
        full_date = new Date(full_date_string);
        this_year_bday = new Date(this_year_bday_string);
    }

    function calculateAge (bday) {
        var ageDifMs = Date.now() - bday.getTime();
        var ageDate = new Date(ageDifMs);
        return Math.abs(ageDate.getUTCFullYear() - 1970);
    }

    function check_if_has_birthday (bday) {
        return (begin.getTime() <= bday.getTime() && bday.getTime() <= (end.getTime()+ (3600000 * 24)));
    }


});