// updateCalibrationData.js

function updateCalibrationData(valueID, valueVAL) {
    fetch('/update_calibration_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            valueID: valueID,
            valueVAL: valueVAL,
        }),
    })
    .then(response => response.json())
    .then(data => {
        // console.log('veriveri:', data);
        if (data && data.status === 'success') {
            localStorage.setItem(valueID, valueVAL);
        } else {
            console.error('Data update failed:', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


