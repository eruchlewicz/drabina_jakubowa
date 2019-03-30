$(document).ready(function () {

    var batch_people = $('#id_batch_people').text();
    var all_batch_people = $('#all_batch_people');
    var batch_people_json = JSON.parse(batch_people);
    var content = "";

    for(var i in batch_people_json){
        content += '<div class="col-lg-4 col-md-4 col-sm-6 float-left"><span class="bold">'+batch_people_json[i].batch+'</span>';
        content += '<br />';
        content += "Mężczyźni: "+batch_people_json[i].men;
        content += '<br />';
        content += "Mężczyźni na wózkach: "+batch_people_json[i].men_wheelchair;
        content += '<br />';
        content += "Kobiety: "+batch_people_json[i].women;
        content += '<br />';
        content += "Kobiety na wózkach: "+batch_people_json[i].women_wheelchair;
        content += '<br /><br /></div>';
    }

    all_batch_people.append(content);


});