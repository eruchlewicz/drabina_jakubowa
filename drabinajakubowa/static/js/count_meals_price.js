$(document).ready(function () {
    $("#id_full_cost").parent().parent().addClass('hidden');

    var total_price = $('#total_price');
    var begin_date = $('#id_begin_date');
    var end_date = $('#id_end_date');
    var price_breakfast = parseFloat($('#Sniadanie_12').text());
    var price_dinner = parseFloat($('#Obiad_12').text());
    var price_supper = parseFloat($('#Kolacja_12').text());
    var price_breakfast_kid = parseFloat($('#Sniadanie_3-11').text());
    var price_dinner_kid = parseFloat($('#Obiad_3-11').text());
    var price_supper_kid = parseFloat($('#Kolacja_3-11').text());
    var adults = $('#id_adults').val();
    var kids = $('#id_kids').val();

    total_price.text($("#id_full_cost").val());

    var pre_diff;

    // date
    function split_beg_date () {
        var beg_date_val = begin_date.val();
        var split = begin_date.val().split(' ');
        if (split.length > 1){
            beg_date_val = split[0];
        }
        return beg_date_val;
    }

    function split_end_date () {
        var end_date_val = end_date.val();
        var split2 = end_date.val().split(' ');
        if (split2.length > 1){
            end_date_val = split2[0];
        }
        return end_date_val;
    }

    var beg_date_val = split_beg_date();
    var end_date_val = split_end_date();
    var total = 0.00;
    pre_diff = Math.abs(Math.ceil((new Date(beg_date_val) - (new Date(end_date_val))) / 1000 / 60 / 60 / 24));
    calculate(pre_diff);

    // changing begin or end date
    begin_date.change(function () {
        var beg_date_val = split_beg_date();
        var end_date_val = split_end_date();
        pre_diff = Math.abs(Math.ceil((new Date(end_date_val) - (new Date(beg_date_val))) / 1000 / 60 / 60 / 24));
        calculate(pre_diff);
    });

    end_date.change(function () {
        var beg_date_val = split_beg_date();
        var end_date_val = split_end_date();
        pre_diff = Math.abs(Math.ceil((new Date(end_date_val) - (new Date(beg_date_val))) / 1000 / 60 / 60 / 24));
        calculate(pre_diff);
    });

    $('#id_adults').change(function () {
        adults = $('#id_adults').val();
        calculate(pre_diff);
    });

    $('#id_kids').change(function () {
        kids = $('#id_kids').val();
        calculate(pre_diff);
    });

    function count_meal_cost (person_type) {
        if(person_type === "kid") return price_breakfast_kid + price_dinner_kid + price_supper_kid;
        else return price_breakfast + price_dinner + price_supper;
    }

    // calculating price, warning: different room and age prices...
    function calculate(diff) {
        if (diff === -0 || diff === 0) {
            total = 0.00;
        } else if (diff > 0) {
            total = (adults * count_meal_cost("adult") + kids * count_meal_cost("kid")) * diff;
        } else {
            total_price.text('--');
            return;
        }
        total_price.text(total.toFixed(2));
        $("#id_full_cost").val(total.toFixed(2));
    }
});