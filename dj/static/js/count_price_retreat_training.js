$(document).ready(function () {
    $("#id_total_cost").parent().parent().addClass('hidden');
    $("#id_total_cost").prop('readonly', true);

    var total_price = $('#total_price');
    var training_id = $('#id_retreat_or_music_training'); // pobranie id z select value
    var accommodation = $('#id_accommodation');
    var saturday_sunday = $('#id_saturday_sunday');
    var total = 0.00;
    var base_price = 0.00;
    var sleeping_bag_price = 0.00;
    var nights_price = 0.00;
    var additional_night = 0.00;
    var training_price = 0.00;
    var add_night_price = 0.00;
    var with_accommodation = true;
    var with_additional_night = true;

    var prices_json_input = $('#prices_json');
    if(prices_json_input.text().length !== 0) var prices_json = JSON.parse(prices_json_input.text());

    get_data ();
    calculate();

    $('#id_retreat_or_music_training').change(function () {
        get_data ();
        check_if_accommodation_included();
        check_if_additional_night_included()
        get_accomodation();
        calculate();
    });

    $('#id_accommodation').change(function () {
        get_data ();
        get_accomodation();
        calculate();
    });

    $('#id_saturday_sunday').change(function () {
        get_data ()
        get_accomodation();
        calculate();
    });

    function get_prices (id) {
        for(var i in prices_json){
            id = parseInt(id);
            if(prices_json[i].id === id) {
                base_price = prices_json[i].base_price;
                sleeping_bag_price = prices_json[i].sleeping_bag_price;
                nights_price = prices_json[i].nights_price;
                additional_night = prices_json[i].additional_night;
                with_accommodation = prices_json[i].with_accommodation;
                with_additional_night = prices_json[i].with_additional_night;
            }
        }
    }

    function check_if_accommodation_included() {
        if(!with_accommodation) {
            accommodation = $('#id_accommodation');
            document.getElementById("id_accommodation").selectedIndex = "1";
            accommodation.parent().parent().addClass('hidden');
        }
        else {
            accommodation = $('#id_accommodation');
            document.getElementById("id_accommodation").selectedIndex = "0";
            accommodation.parent().parent().removeClass('hidden');
        }
    }

    function check_if_additional_night_included() {
        if(!with_additional_night) {
            saturday_sunday = $('#id_saturday_sunday');
            document.getElementById("id_saturday_sunday").selectedIndex = "1";
            saturday_sunday.parent().parent().find( "span" ).addClass('hidden');
            saturday_sunday.parent().addClass('hidden');
            $('label[for="id_saturday_sunday"]').parent().addClass('hidden');
        }
        else {
            saturday_sunday = $('#id_saturday_sunday');
            document.getElementById("id_saturday_sunday").selectedIndex = "1";
            saturday_sunday.parent().parent().find( "span" ).removeClass('hidden');
            saturday_sunday.parent().removeClass('hidden');
            $('label[for="id_saturday_sunday"]').parent().removeClass('hidden');
        }
    }

    function get_data () {
        training_id = $('#id_retreat_or_music_training').val();
        get_prices(training_id);
    }

    function get_accomodation () {
        accommodation = $('#id_accommodation').val();
        if(accommodation === 'N') training_price = base_price;
        else if(accommodation === 'S') training_price = sleeping_bag_price;
        else if (accommodation === 'L') training_price = nights_price;
        saturday_sunday = $('#id_saturday_sunday').val();
        if(saturday_sunday === 'T') add_night_price = additional_night;
        else add_night_price = 0.00;
    }

    function calculate() {
        if (training_id.length !== 0 && accommodation.length !== 0  && saturday_sunday.length !== 0) {
            total = training_price + add_night_price;
        } else {
            total_price.text('---');
            return;
        }
        total_price.text(total.toFixed(2) + " zł");
        $("#id_total_cost").val(total.toFixed(2));
    }
});