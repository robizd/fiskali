// Declace vars
let myChart;
let csrftoken;

// Get cookie
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

csrftoken = getCookie('csrftoken');

// Listener za dropdown
document.getElementById("vrijeme-chart").addEventListener("change", function (e) {
    let vrijeme = this.options[this.selectedIndex].value;
    console.log('Selecktiran je: ' + vrijeme);
    periodAjax(vrijeme);

});


// Dohvat podataka sa backend-a
function periodAjax(vrijeme) {
    $.ajax({
        type: "GET",
        async: false,
        beforeSend: function (request) {
            request.setRequestHeader("X-CSRFToken", csrftoken);
        },
        url: "/prometChart/" + vrijeme,
        success: function (data) {
            console.log(data);
            result = data;

            switch (vrijeme) {
                case '0':
                    getMjesecniChart(data);
                    break;
                case '1':
                    getSatiChart(data);
                    break;
                case '2':
                    getDnevniChart(data);
                    break;
                case '3':
                    getGodisnjiChart(data);
                    break;
            }
        }
    });
}

// Mjesecni chart
function getMjesecniChart(data) {
    let mjeseci = result.map(function (e) {
        return e.vrijeme_izdavanja__month;
    });

    let promet = result.map(function (e) {
        return e.ukupni_iznos__sum;
    });

    let ctx = document.getElementById('myChart').getContext('2d');

    if(myChart != null){
        myChart.destroy();
    }

    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            // labels: ['Sijecanj', 'Veljaca', 'Ozujak', 'Travanj', 'Svibanj', 'Lipanj', 'Srpanj', 'Kolovoz',
            //     'Rujan', 'Listopad', 'Studeni', 'Prosinac'],
            labels: mjeseci,
            datasets: [{
                label: 'Promet zaposlenika po mjesecima',
                data: promet,
                // data: [1,2,3,4,5,6,7,8,9,10,11,12],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',

                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',

                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });
}

function getSatiChart(data) {
    let sati = result.map(function (e) {
        return e.vrijeme_izdavanja__hour;
    });

    let promet = result.map(function (e) {
        return e.ukupni_iznos__sum;
    });

    if(myChart != null){
        myChart.destroy();
    }

    let ctx = document.getElementById('myChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            // labels: ['Sijecanj', 'Veljaca', 'Ozujak', 'Travanj', 'Svibanj', 'Lipanj', 'Srpanj', 'Kolovoz',
            //     'Rujan', 'Listopad', 'Studeni', 'Prosinac'],
            labels: sati,
            datasets: [{
                label: 'Promet zaposlenika po satima u danu',
                data: promet,
                // data: [1,2,3,4,5,6,7,8,9,10,11,12],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',

                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',

                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });

}

function getDnevniChart(data) {
    let dani = result.map(function (e) {
        return e.vrijeme_izdavanja__day;
    });

    let promet = result.map(function (e) {
        return e.ukupni_iznos__sum;
    });

    if(myChart != null){
        myChart.destroy();
    }

    let ctx = document.getElementById('myChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            // labels: ['Sijecanj', 'Veljaca', 'Ozujak', 'Travanj', 'Svibanj', 'Lipanj', 'Srpanj', 'Kolovoz',
            //     'Rujan', 'Listopad', 'Studeni', 'Prosinac'],
            labels: dani,
            datasets: [{
                label: 'Promet zaposlenika po danima u mjesecu',
                data: promet,
                // data: [1,2,3,4,5,6,7,8,9,10,11,12],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',

                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',

                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });
}

function getGodisnjiChart(data) {
    let godine = result.map(function (e) {
        return e.vrijeme_izdavanja__year;
    });

    let promet = result.map(function (e) {
        return e.ukupni_iznos__sum;
    });

    if(myChart != null){
        myChart.destroy();
    }

    let ctx = document.getElementById('myChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: godine,
            datasets: [{
                label: 'Promet zaposlenika po godinama',
                data: promet,
                // data: [1,2,3,4,5,6,7,8,9,10,11,12],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',

                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',

                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });

}

function getMjesecniChartInitial() {
    let result;
    $.ajax({
        type: "GET",
        async: false,
        beforeSend: function (request) {
            request.setRequestHeader("X-CSRFToken", csrftoken);
        },
        url: "/prometChart/0",
        success: function (data) {
            console.log(data);
            result = data;
        }
    });

    let mjeseci = result.map(function (e) {
        return e.vrijeme_izdavanja__month;
    });

    let promet = result.map(function (e) {
        return e.ukupni_iznos__sum;
    });

    let ctx = document.getElementById('myChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            // labels: ['Sijecanj', 'Veljaca', 'Ozujak', 'Travanj', 'Svibanj', 'Lipanj', 'Srpanj', 'Kolovoz',
            //     'Rujan', 'Listopad', 'Studeni', 'Prosinac'],
            labels: mjeseci,
            datasets: [{
                label: 'Promet zaposlenika po mjesecima',
                data: promet,
                // data: [1,2,3,4,5,6,7,8,9,10,11,12],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',

                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',

                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });
}

getMjesecniChartInitial();




