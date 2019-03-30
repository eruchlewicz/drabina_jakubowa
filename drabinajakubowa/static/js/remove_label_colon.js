document.addEventListener("DOMContentLoaded", function() {

    var labels = document.querySelectorAll("label");
    for(var i=0; i<labels.length; i++){
        var label = labels[i].textContent.slice(0,-1);
        labels[i].textContent = label;
    }

});