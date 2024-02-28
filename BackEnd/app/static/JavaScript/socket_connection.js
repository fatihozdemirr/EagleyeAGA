document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    // Elementin value'sunu güncelleyen yardımcı fonksiyon
    function updateElementValueById(id, value, digits = 2) {
        try{
            const element = document.getElementById(id);
            //if (element) element.value = value.toFixed(digits);
            if (element) {
                if (element.tagName.toLowerCase() === 'input') {
                    element.value = value.toFixed(digits);
                } else {
                    const spanElement = element.querySelector('span');
                    if (spanElement) {
                        spanElement.textContent = value.toFixed(digits);
                    }
                }
            }
        } catch (error) {
            console.error('Element değeri güncelleme hatası:', error);
        }
    }

    socket.on('sensor_data', function(data) {
        try{
            updateElementValueById('CO_inputoffset', data.co_offset);
            updateElementValueById('CO2_inputoffset', data.co2_offset, 3);
            updateElementValueById('CH4_inputoffset', data.ch4_offset);

            updateElementValueById('CO_reading', data.co_read);
            updateElementValueById('CO2_reading', data.co2_read, 3);
            updateElementValueById('CH4_reading', data.ch4_read);

            updateElementValueById('CO_value', data.co_result);
            updateElementValueById('CO2_value', data.co2_result, 3);
            updateElementValueById('CH4_value', data.ch4_result);

            updateElementValueById('input7', data.Temperature,1);
            updateElementValueById('input8', data.CH4_Factor,1);
            updateElementValueById('input9', data.Alloy_Factor,1);
            updateElementValueById('input10', data.H2,1);

            updateElementValueById('CO_reading_popup', data.co_read);
            updateElementValueById('CO2_reading_popup', data.co2_read, 3);
            updateElementValueById('CH4_reading_popup', data.ch4_read);

            updateElementValueById('CO_Referance_Value', data.co_referance,0);
            updateElementValueById('CO2_Referance_Value', data.co2_referance,0);
            updateElementValueById('CH4_Referance_Value', data.ch4_referance,0);
        } catch (error) {
            console.error('WebSocket veri işleme hatası:', error);
        }
    });
});
