$('#artikl-select2').select2({
    ajax: {
        url: 'artikl',
        dataType: 'json',
        delay: 250
    },
     placeholder: 'Upišite artikl',
});


$('#kupac-select2').select2({
    ajax: {
        url: 'kupac',
        dataType: 'json',
        delay: 250
    },
     placeholder: 'Upišite kupca',
});


$('#poslovnica-select2').select2({
    ajax: {
        url: 'poslovnica',
        dataType: 'json',
        delay: 250
    },
     placeholder: 'Upišite poslovnicu',
});

