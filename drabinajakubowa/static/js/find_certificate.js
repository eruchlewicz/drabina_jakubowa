$(document).ready(function () {
    var batch_volunteers_json = $('#certificates_json').text();
    var batch_participants_json = $('#participant_certificates_json').text();
    var certificate_input = $("#id_certificate");
    var participant_certificate_input = $("#id_participant_certificate");
    var certificate_val = certificate_input.val();
    var participant_certificate_val = participant_certificate_input.val();
    var btn_find = $("#btn_find");
    var btn_find_participant = $("#btn_find_participant");
    var batch_volunteer_input = $("#id_batch_volunteer");
    var batch_volunteer = "";
    var batch_volunteers = JSON.parse(batch_volunteers_json);
    var batch_participant_input = $("#id_batch_participant");
    var batch_participant = "";
    var batch_participants = JSON.parse(batch_participants_json);

    function find (input) {
        for(var i in batch_volunteers){
            if(String(batch_volunteers[i].unique_key) === input) {
                batch_volunteer = batch_volunteers[i];
                var begin = batch_volunteer.batch_begin_date.slice(0,10).replace(/-/g, ".");
                var end = batch_volunteer.batch_end_date.slice(0,10).replace(/-/g, ".");
                var batch_days_hours = batch_volunteer.batch_days * 14;
                var nights_hours = batch_volunteer.nights * 9;
                var training_days = batch_volunteer.training_days;
                var training_duration = batch_volunteer.batch__training_duration;
                var hours_sum = batch_days_hours + nights_hours;
                if(training_days >= 1) {
                    hours_sum += training_duration;
                }
                batch_volunteer_input.append(batch_volunteer.volunteer__name + " " + batch_volunteer.volunteer__surname +
                    '<br />' + batch_volunteer.batch__name + " " + batch_volunteer.batch__institution__city + '<br />'
                    + begin + " - " + end + '<br />' + "Suma godzin: " + hours_sum);
                batch_volunteer = "";
                break;

            }
        }
        if (batch_volunteer.length === 0) batch_volunteer_input.append("Nie znaleziono.");
    }

    function findParticipant (input) {
        for(var i in batch_participants){
            if(String(batch_participants[i].unique_key) === input) {
                batch_participant = batch_participants[i];
                var begin = batch_participant.batch__begin_date.slice(0,10).replace(/-/g, ".");
                var end = batch_participant.batch__end_date.slice(0,10).replace(/-/g, ".");
                batch_participant_input.append(batch_participant.participant__name + " " + batch_participant.participant__surname +
                    '<br />' + batch_participant.batch__name + " " + batch_participant.batch__institution__city + '<br />'
                    + begin + " - " + end);
                batch_participant = "";
                break;

            }
        }
        if (batch_participant.length === 0) batch_participant_input.append("Nie znaleziono.");
    }

    certificate_input.change(function () {
        certificate_val = $("#id_certificate").val();
    });

    participant_certificate_input.change(function () {
        participant_certificate_val = $("#id_participant_certificate").val();
    });

    btn_find.click(function () {
        console.log("wolontariusz");
        batch_volunteer_input.empty();
        find(certificate_val);
    });

    btn_find_participant.click(function () {
        console.log("podopieczny");
        batch_participant_input.empty();
        findParticipant(participant_certificate_val);
    });

});