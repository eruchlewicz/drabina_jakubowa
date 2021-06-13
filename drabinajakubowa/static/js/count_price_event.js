$(document).ready(function () {
    $("#id_total_cost").parent().parent().addClass('hidden');
    $("#id_total_cost").prop('readonly', true);

    var total_price = $('#total_price');
    var event_id = $('#id_event'); // pobranie id z select value
    var total = 0.00;
    var price = 0.00;

    var prices_json_input = $('#prices_json');
    if(prices_json_input.text().length !== 0) var prices_json = JSON.parse(prices_json_input.text());

    get_data ();
    calculate();

    $('#id_event').change(function () {
        get_data ();
        calculate();
    });

    function get_prices (id) {
        for(var i in prices_json){
            id = parseInt(id);
            if(prices_json[i].id === id) price = prices_json[i].price;
        }
    }

    function get_data () {
        event_id = $('#id_event').val();
        get_prices(event_id);
    }

    function calculate() {
        if (event_id.length !== 0) {
            total = price;
        } else {
            total_price.text('---');
            return;
        }
        total_price.text(total.toFixed(2) + " zł");
        $("#id_total_cost").val(total.toFixed(2));
    }
});