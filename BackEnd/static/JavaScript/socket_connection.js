document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    // Elementin value'sunu güncelleyen yardımcı fonksiyon
    function updateElementValueById(id, value, digits = 2) {
        const element = document.getElementById(id);
        if (element) element.value = value.toFixed(digits);
    }

    socket.on('sensor_data', function(data) {
        // Her bir input için value güncelleme işlemini tek satırda yap
        updateElementValueById('CO_inputoffset', data.co_offset);
        updateElementValueById('CO2_inputoffset', data.co2_offset, 3);
        updateElementValueById('CH4_inputoffset', data.ch4_offset);

        updateElementValueById('CO_reading', data.co_read);
        updateElementValueById('CO2_reading', data.co2_read, 3);
        updateElementValueById('CH4_reading', data.ch4_read);

        updateElementValueById('CO_value', data.co_result);
        updateElementValueById('CO2_value', data.co2_result, 3);
        updateElementValueById('CH4_value', data.ch4_result);
    });
});
