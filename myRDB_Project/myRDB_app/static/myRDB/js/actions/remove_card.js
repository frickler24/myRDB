function remove_current_card(form, card){
    console.log(form);
    console.log(card);
    var inputs = form.serializeArray();
    console.log(inputs);
    var id = card[0].id;
    var remove_confirm;
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
        }
    });
    var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"action_type":"remove_from_requests","requesting_user":inputs[1]['value'],"request_pk":inputs[0]['value']};
    var successful=false;

    remove_confirm = confirm("Anfrage aus Listung entfernen?");
    if(remove_confirm){
        $.ajax({type:'POST',
                data:data,
                url:'http://127.0.0.1:8000/users/'+inputs[1]['value']+'/',
                async:false,
                success: function(res){console.log(res);
                    successful=true},
                error: function(res){console.log(res);}
            });
        if (successful) {
            $.ajax({type:'DELETE',
                data:data,
                url:'http://127.0.0.1:8000/changerequests/'+inputs[0]['value']+'/',
                async:false,
                success: function(res){console.log(res);
                    successful=true},
                error: function(res){console.log(res);}
            });
            if (successful) {
                $('#'+id).remove();
                alert("Request erfolgreich aus Listung\nund Requestpool entfernt!")
            }
            else{
                alert("Beim Entfernen aus Requestpool\nist ein Fehler aufgetreten!")
            }
        }
        else{
            alert("Beim Entfernen aus Listung\nist ein Fehler aufgetreten!")
        }
    }


}


function remove_card_clicked(d) {
    var form = $(d);
    var current_card = $(d.parentElement.parentElement.parentElement.parentElement);
    remove_current_card(form,current_card);
   return false;
}