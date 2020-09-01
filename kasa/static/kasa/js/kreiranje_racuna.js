var doAjax = true;

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

function ukupno() {
    if (doAjax) {
        doAjax = false;
        var csrftoken = getCookie('csrftoken');

        console.log($('#novi-racun').serialize());

        $.ajax({
            type: "POST",
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            url: "/ukupnoAjax",
            data: $('#novi-racun').serialize(),
            success: function (data) {
                $('#osnovica').html(data.osnovica);
                $('#porez').html(data.porez);
                $('#ukupno').html(data.ukupno);
            },
            complete: function (data) {
                doAjax = true
            }
        });
    }
}

$("input[id*='stavkaracuna']").change(function () {
    // window.setTimeout(ukupno, 1000);
    ukupno();
});

$("input[id*='stavkaracuna']").keypress(function () {
    ukupno();
});

function setMjernaJedinicaListener() {
    ukupno();

    let elements = document.getElementsByClassName("artikl");

    for (let i = 0; i < elements.length; i++) {
        elements[i].onchange = function (e) {
            var csrftoken = getCookie('csrftoken');

            inputID = this.id.replace("artikl", "jedinica");

            $.ajax({
                type: "GET",
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                },
                url: "/dohvatJediniceArtikla",
                data: "artikal=" + this.value,
                success: function (data) {
                    document.getElementById(inputID).value = data.jedinica;
                },
            })
        };
    }
}

// Postavi listener za prvu default stavku
setMjernaJedinicaListener();

$('.formset_row').formset({
    addText: 'Dodaj stavku',
    deleteText: 'Izbriši',
    deleteCssClass: 'btn btn-danger izbrisi',
    addCssClass: 'btn btn-info',
    prefix: 'stavkaracuna_set',
    removed: ukupno,
    added: setMjernaJedinicaListener,
});



