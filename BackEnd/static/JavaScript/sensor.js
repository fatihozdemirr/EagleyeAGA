// let sensorData = {
//     reading_1: '',
//     reading_2: '',
//     reading_3: ''
// };

// function updateSensorData() {
//     // let globalReadingID, globalReadingVAL;
//     $.ajax({
//         type: 'GET',
//         url: '/get_sensor_values',
//         success: function(data) {
//             sensorData.reading_1 = data.co;
//             sensorData.reading_2 = data.co2;
//             sensorData.reading_3 = data.ch4;

//             // const readings = {
//             //     reading_1: sensorData.reading_1,
//             //     reading_2: sensorData.reading_2,
//             //     reading_3: sensorData.reading_3
//             // };
            
//             // for (const [readingID, readingVAL] of Object.entries(readings)) {
//             //     console.log('readingID:', readingID);
//             //     console.log('readingVAL:', readingVAL);

//             //     if (readingID && readingVAL !== undefined) {   /// 
//             //         globalReadingID = readingID;
//             //         globalReadingVAL = readingVAL;
//             //         fetch('/update_calibration_data', {
//             //             method: 'POST',
//             //             headers: {
//             //                 'Content-Type': 'application/json',
//             //             },
//             //             body: JSON.stringify({
//             //                 readingID: readingID,
//             //                 readingVAL: readingVAL,
//             //             }),
//             //         })
//             //             .then(response => response.json())
//             //             .then(data => {
//             //                 console.log(data);
//             //             })
//             //             .catch(error => {
//             //                 console.error('Error:', error);
//             //             });
//             //     } else {
//             //         console.error('Invalid inputIdchange.');
//             //     }
//             // } 

//             // Güncelleme işlemleri burada yapılır
//             updateCalibrationInputs(data);
//         },
//         error: function() {
//             console.error('Sensor data request failed.');
//         }
//     });
// }
// $(document).ready(function() {
//     updateSensorData();
//     setInterval(updateSensorData, 1000);  
// });

// function updateCalibrationInputs() {
//     $('#CO_reading').val(parseFloat(sensorData.reading_1).toFixed(2));
//     $('#CO2_reading').val(parseFloat(sensorData.reading_2).toFixed(3));
//     $('#CH4_reading').val(parseFloat(sensorData.reading_3).toFixed(2));
//     // $('#input1').val(parseFloat(sensorData.reading_1).toFixed(2));
//     // $('#input2').val(parseFloat(sensorData.reading_2).toFixed(3));
//     // $('#input3').val(parseFloat(sensorData.reading_3).toFixed(2));   
// }
