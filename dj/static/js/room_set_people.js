$(document).ready(function () {

    $("#id_full_cost").parent().parent().addClass('hidden');
    $('#id_adults').parent().parent().addClass('hidden');
    $('#id_kids').parent().parent().addClass('hidden');
    $('#id_who_where').parent().parent().addClass('hidden');
    $('#id_begin_date').parent().parent().addClass('hidden');
    $('#id_end_date').parent().parent().addClass('hidden');


    var total_price = $('#total_price');
    var begin_date = $('#id_begin_date');
    var end_date = $('#id_end_date');
    var room_input = $("#id_room");
    var rooms_numbers = [];
    var meals = $('#id_meals');
    var price_breakfast = parseFloat($('#Sniadanie_12').text());
    var price_dinner = parseFloat($('#Obiad_12').text());
    var price_supper = parseFloat($('#Kolacja_12').text());
    var price_breakfast_kid = parseFloat($('#Sniadanie_3-11').text());
    var price_dinner_kid = parseFloat($('#Obiad_3-11').text());
    var price_supper_kid = parseFloat($('#Kolacja_3-11').text());
    var price_kid_floor = parseFloat($('#Pokoj_3-11').text());
    var price_floor = parseFloat($('#Pokoj_12').text());
    var price_basement = parseFloat($('#Pokoj_piwnica_12').text());
    var price_kid_basement = parseFloat($('#Pokoj_piwnica_3-11').text());
    var adults = $('#id_adults');
    var kids = $('#id_kids');
    var rooms_input = $('#all_rooms_json').text();
    var who_where_input = $('#id_who_where');
    var who_where = "";
    var setting = $('#id_for_setting');
    var button_count = $('#id_count_rooms_people');
    var adults_from_rooms = 0;
    var kids_from_rooms = 0;
    var rooms_json = JSON.parse(rooms_input);

    if(who_where_input.text().length !== 0) var who_where_json = JSON.parse(who_where_input.text());

    total_price.text($("#id_full_cost").val());

    var pre_diff;

    function fill_in_people () {
        for(var i in who_where_json){
            $("#adults" + who_where_json[i].number).val(who_where_json[i].adults);
            $("#kids" + who_where_json[i].number).val(who_where_json[i].kids);
        }
    }

    // date
    function split_beg_date () {
        var beg_date_val = begin_date.val();
        var split = begin_date.val().split(' ');
        if (split.length > 1){
            beg_date_val = split[0];
        }
        beg_date_val = beg_date_val.split(".");
        return beg_date_val[2]+"-"+beg_date_val[1]+"-"+beg_date_val[0];
    }

    function split_end_date () {
        var end_date_val = end_date.val();
        var split2 = end_date.val().split(' ');
        if (split2.length > 1){
            end_date_val = split2[0];
        }
        end_date_val = end_date_val.split(".");
        return end_date_val[2]+"-"+end_date_val[1]+"-"+end_date_val[0];
    }

    function get_beds_count (room_number) {
        var beds = 0;
        for(var i in rooms_json){
            if(rooms_json[i].number === room_number) beds = rooms_json[i].beds_number;
        }
        return beds;
    }


    function create_inputs_for_rooms () {
        setting.empty();
        rooms_numbers = get_rooms();

        for(var i=0; i<rooms_numbers.length; i++){
            var label = document.createElement("label");
            var label2 = document.createElement("label");
            var label3 = document.createElement("label");
            label.className = "bold float-left";
            label2.className = "float-left m-r-10 p-l-0 m-t-5";
            label3.className = "float-left m-r-10 m-t-5";
            label2.textContent = "Dorośli/młodzież:";
            label3.textContent = "Dzieci 2+:";
            var input = document.createElement("input");
            var input2 = document.createElement("input");
            input.type = "number";
            input.value = 0;
            input2.type = "number";
            input2.value = 0;
            input.className = "form-control small-nr-input";
            input2.className = "form-control small-nr-input";
            label.textContent = "Pokój: " + rooms_numbers[i];
            setting.append(label);
            setting.append('<br />');
            setting.append('<hr />');
            setting.append(label2);
            input.id = "adults" + rooms_numbers[i];
            setting.append(input);
            setting.append('<div class="row h-10"></div>');
            setting.append(label3);
            input2.id = "kids" + rooms_numbers[i];
            setting.append(input2);
            setting.append('<br />');
            $('#adults'+rooms_numbers[i]).attr({"max" : get_beds_count(rooms_numbers[i]), "min" : 0});
            $('#kids'+rooms_numbers[i]).attr({"max" : get_beds_count(rooms_numbers[i]), "min" : 0});
        }
    }

    var beg_date_val = split_beg_date();
    var end_date_val = split_end_date();
    var total = 0.00;
    pre_diff = Math.abs(Math.ceil((new Date(beg_date_val) - (new Date(end_date_val))) / 1000 / 60 / 60 / 24));  

    function get_rooms () {
        rooms_numbers = [];
        $("#id_room option:selected").each(function () {
            var $this = $(this);
            var selText = $this.text();
            rooms_numbers.push(selText);
        });
        return rooms_numbers;
    }

    function if_basement (room) {
        return (room.charAt(0) === 'p');
    }

    function count_single_room_price (room) {
        var room_total_price = 0;
        var room_adults = parseInt($('#adults' + room).val());
        var room_kids = parseInt($('#kids' + room).val());
        who_where += "{\"number\": \"" + room + "\", \"adults\": " + room_adults + ", \"kids\": " + room_kids + "}";
        if(meals.is(":checked")){
            if(if_basement(room)) {
                adults_from_rooms += room_adults;
                kids_from_rooms += room_kids;
                room_total_price = room_adults * (price_basement + count_meal_cost("adult"))
                    + room_kids * (price_kid_basement + count_meal_cost("kid"));
            }
            else {
                adults_from_rooms += room_adults;
                kids_from_rooms += room_kids;
                room_total_price = room_adults * (price_floor + count_meal_cost("adult"))
                    + room_kids * (price_kid_floor + count_meal_cost("kid"));
            }
        }
        else {
            if(if_basement(room)) {
                adults_from_rooms += room_adults;
                kids_from_rooms += room_kids;
                room_total_price = room_adults * price_basement + room_kids * price_kid_basement;
            }
            else {
                adults_from_rooms += room_adults;
                kids_from_rooms += room_kids;
                room_total_price = room_adults * price_floor + room_kids * price_kid_floor;
            }
        }
        return room_total_price;
    }

    function check_all_rooms () {
        adults_from_rooms = 0;
        kids_from_rooms = 0;
        who_where = "[";
        var total_rooms_prices = 0;
        var room_numbers = get_rooms();
        for(var i=0; i<room_numbers.length; i++){
            total_rooms_prices += count_single_room_price(room_numbers[i]);
            if(i<room_numbers.length-1) who_where += ", ";
        }
        who_where += "]";
        who_where_input.text(who_where);
        return total_rooms_prices;
    }

    create_inputs_for_rooms();
    fill_in_people();
    calculate(pre_diff);

    button_count.click(function () {
        calculate(pre_diff);
    });

    // changing rooms
    room_input.change(function () {
        create_inputs_for_rooms();
    });

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

    meals.change(function () {
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
            total = Math.ceil(price_floor * 0.75);
        } else if (diff > 0) {
            total = check_all_rooms() * diff;
            if(meals.is(":checked")) {
                var adults_30 = parseInt(adults_from_rooms/30);
                var gratis = adults_30 * (price_floor + price_breakfast + price_dinner + price_supper);
                total -= gratis * diff;
            }
        } else {
            total_price.text('--');
            return;
        }
        total_price.text(total.toFixed(2));
        $("#id_full_cost").val(total.toFixed(2));
        $("#id_adults").val(adults_from_rooms);
        $("#id_kids").val(kids_from_rooms);
    }
});