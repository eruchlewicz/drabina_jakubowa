$(document).ready(function () {
    $("#id_total_cost").parent().parent().addClass('hidden');
    $("#id_total_cost").prop('readonly', true);

    var total_price = $('#total_price');
    var training_id = $('#id_retreat_or_music_training'); // pobranie id z select value
    var accommodation = $('#id_accommodation');
    var total = 0.00;
    var base_price = 0.00;
    var sleeping_bag_price = 0.00;
    var nights_price = 0.00;
    var training_price = 0.00;

    var prices_json_input = $('#prices_json');
    if(prices_json_input.text().length !== 0) var prices_json = JSON.parse(prices_json_input.text());

    get_data ();
    calculate();

    $('#id_retreat_or_music_training').change(function () {
        get_data ();
        calculate();
    });

    $('#id_accommodation').change(function () {
        get_data ();
        calculate();
    });

    function get_prices (id) {
        for(var i in prices_json){
            id = parseInt(id);
            if(prices_json[i].id === id) {
                base_price = prices_json[i].base_price;
                sleeping_bag_price = prices_json[i].sleeping_bag_price;
                nights_price = prices_json[i].nights_price;
            }
        }
    }

    function get_data () {
        training_id = $('#id_retreat_or_music_training').val();
        get_prices(training_id);
        accommodation = $('#id_accommodation').val();
        if(accommodation === 'N') training_price = base_price;
        else if(accommodation === 'S') training_price = sleeping_bag_price;
        else if (accommodation === 'L') training_price = nights_price;
    }

    function calculate() {
        if (training_id.length !== 0 && accommodation.length !== 0) {
            total = training_price;
        } else {
            total_price.text('---');
            return;
        }
        total_price.text(total.toFixed(2) + " zł");
        $("#id_total_cost").val(total.toFixed(2));
    }
});