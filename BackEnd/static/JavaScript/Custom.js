// document.addEventListener('DOMContentLoaded', function() {
//     // Sayfa yüklendiğinde çalışacak kodlar
    
//     // Sayfa yüklendiğinde toggle switch durumunu al
//     const toggleStatusFromServer = "{{ toggle_status }}";

//     // Toggle'ı duruma göre ayarla
//     const togglememory = document.getElementById('myToggle');
//     if (toggleStatusFromServer === 'F') {
//         // Eğer toggle switch "F" ise
//         togglememory.checked = true;
//     } else {
//         // Eğer toggle switch "C" ise
//         togglememory.checked = false;
//     }

//     // Input elementini seç
//     const temp = document.getElementById('input7');
//     console.log('tempfirst:', temp.value);

//     // Toggle elementini seç
//     const toggle = document.querySelector('.toggle input');

//     // Toggle durumu değiştiğinde çalışacak fonksiyon
//     toggle.addEventListener('change', function() {
//         // Toggle'ın durumuna göre input değerini güncelle
//         if (toggle.checked) {
//             temp.value = (((parseFloat(temp.value) * 9) / 5) + 32).toFixed(1);
//             console.log('Toggle is checked. fahrenheit:', temp.value);

//             // Veritabanına göndermek için JSON nesnesi oluştur
//             const dataToSend = {
//                 input_id: 'input7',
//                 new_value: temp.value,
//                 toggle_status: 'F',
//             };

//             // Eğer TempUnit değeri için bir değer belirlenmemişse, varsayılan bir değer atayın
//             if (dataToSend.toggle_status === 'F' && !dataToSend.TempUnit) {
//                 dataToSend.TempUnit = 'F'; // veya başka bir varsayılan değer
//             }

//             sendToServer(dataToSend);

//         } else {
//             temp.value = (((parseFloat(temp.value) - 32) * 5) / 9).toFixed(1);
//             console.log('Toggle is not checked. celcius:', temp.value);

//             // Veritabanına göndermek için JSON nesnesi oluştur
//             const dataToSend = {
//                 input_id: 'input7',
//                 new_value: temp.value,
//                 toggle_status: 'C',
//             };

//             // Eğer TempUnit değeri için bir değer belirlenmemişse, varsayılan bir değer atayın
//             if (dataToSend.toggle_status === 'C' && !dataToSend.TempUnit) {
//                 dataToSend.TempUnit = 'C'; // veya başka bir varsayılan değer
//             }

//             sendToServer(dataToSend);
            
//         }
//     });

//     if (togglememory.checked === false || toggle.checked === false) {
//         // formüller ve toggle yapılacak
//         // CO_Value = 20 
//         // CO_Value = 0,5
//         const e = 2.718281828;
//         const C8 = (parseFloat(temp.value) + 273.15).toFixed(2);
//         let log10K2 = -1 * (3.2673 - 8820.69 / C8 - 0.001208714 * C8 + 0.153734 * Math.pow(10, -6) * Math.pow(C8, 2) + 2.295483 * (Math.log(C8) / Math.log(10)));
//         let K2 = Math.pow(10, log10K2)
//         let a = (((Math.pow(20, 2) / 0.5) * K2) / 100);
//         let Xc1 = a / (1.07 * Math.pow(e, (4798.6 / C8)));
//         const alloy = document.getElementById('input9').value;
//         let XcAF = a / (1.07 * alloy * Math.pow(10, (3751 / (C8 * 1.8 )))/100); 
//         let CarbonAF = ((XcAF / (1 + 19.6 * XcAF))*100).toFixed(2);
//         // Carbon //
//         let Carbon = ((Xc1 / (1 + 19.6 * Xc1))*100).toFixed(2);
//         console.log('Carbon:', Carbon);
//         const input5Element = document.getElementById("input5");
//         input5Element.value = Carbon;

//         let Z3 = (0.0107 * Math.pow(e, (4798.6 / C8)));
//         let AF3 = -(3.2673 - 8820.69/C8 - 0.001208714 * C8 + 0.153734 * 0.000001 * Math.pow(C8, 2) + 2.295483 * (Math.log(C8) / Math.log(10)));
//         let AC3 = 36.72508 - 3994.704 / C8 + 0.004462408 * C8 - 0.671814 * 0.000001 * Math.pow(C8, 2) - 12.220277 * (Math.log(C8) / Math.log(10));
//         let AI3 = (Math.pow(10, AF3) * Math.pow(10, AC3));

//         /////////////// AA3 te sonuç birebir çıkmadı, tekrar bakılacak ///////////////

//         let AA3 = (alloy/100) * Z3 * (Carbon * 100)/100;   
//         console.log('AA3:', AA3);

//         const H2variable = document.getElementById('input10').value;
//         // H2O //
//         let H20 = ((20 * H2variable / AA3 * AI3) / 100).toFixed(2); 
//         const input11Element = document.getElementById("input11");
//         input11Element.value = H20;

//         let AT31 = Math.pow(10, (2.9419064318711 - 13007.7694364901 / C8)) * H20 / H2variable; 
//         let AT3 = Math.pow(AT31,2); 
//         // O2 //   
//         let O2 = (-0.0275 * C8 * 1.8 * (Math.log(AT3 / 0.209) / Math.log(10))).toFixed(2);
//         const input6Element = document.getElementById("input6");
//         input6Element.value = O2;
//         let AO3 = (4238.7/(6.3979 - (Math.log(H20/100) / Math.log(10)))) - 460;
//         // Dew //   
//         let AP3 = ((AO3 - 32) / 1.8).toFixed(2);
//         const input12Element = document.getElementById("input12");
//         input12Element.value = AP3;
//     }

//     document.getElementById('input7').addEventListener('click', function() {
//         document.querySelector('.numpad .enter').addEventListener('click', function () {
//             openKeyboard('input7');
//             if (togglememory.checked === false || toggle.checked === false) {
//                 // formüller ve toggle yapılacak
//                 // CO_Value = 20 
//                 // CO_Value = 0,5
//                 const e = 2.718281828;
//                 const C8 = (parseFloat(temp.value) + 273.15).toFixed(2);
//                 let log10K2 = -1 * (3.2673 - 8820.69 / C8 - 0.001208714 * C8 + 0.153734 * Math.pow(10, -6) * Math.pow(C8, 2) + 2.295483 * (Math.log(C8) / Math.log(10)));
//                 let K2 = Math.pow(10, log10K2)
//                 let a = (((Math.pow(20, 2) / 0.5) * K2) / 100);
//                 let Xc1 = a / (1.07 * Math.pow(e, (4798.6 / C8)));
//                 const alloy = document.getElementById('input9').value;
//                 let XcAF = a / (1.07 * alloy * Math.pow(10, (3751 / (C8 * 1.8 )))/100); 
//                 let CarbonAF = ((XcAF / (1 + 19.6 * XcAF))*100).toFixed(2);
//                 // Carbon //
//                 let Carbon = ((Xc1 / (1 + 19.6 * Xc1))*100).toFixed(2);
//                 console.log('Carbon:', Carbon);
//                 const input5Element = document.getElementById("input5");
//                 input5Element.value = Carbon;

//                 let Z3 = (0.0107 * Math.pow(e, (4798.6 / C8)));
//                 let AF3 = -(3.2673 - 8820.69/C8 - 0.001208714 * C8 + 0.153734 * 0.000001 * Math.pow(C8, 2) + 2.295483 * (Math.log(C8) / Math.log(10)));
//                 let AC3 = 36.72508 - 3994.704 / C8 + 0.004462408 * C8 - 0.671814 * 0.000001 * Math.pow(C8, 2) - 12.220277 * (Math.log(C8) / Math.log(10));
//                 let AI3 = (Math.pow(10, AF3) * Math.pow(10, AC3));

//                 /////////////// AA3 te sonuç birebir çıkmadı, tekrar bakılacak ///////////////

//                 let AA3 = (alloy/100) * Z3 * (Carbon * 100)/100;   
//                 console.log('AA3:', AA3);

//                 const H2variable = document.getElementById('input10').value;
//                 // H2O //
//                 let H20 = ((20 * H2variable / AA3 * AI3) / 100).toFixed(2); 
//                 const input11Element = document.getElementById("input11");
//                 input11Element.value = H20;

//                 let AT31 = Math.pow(10, (2.9419064318711 - 13007.7694364901 / C8)) * H20 / H2variable; 
//                 let AT3 = Math.pow(AT31,2); 
//                 // O2 //   
//                 let O2 = (-0.0275 * C8 * 1.8 * (Math.log(AT3 / 0.209) / Math.log(10))).toFixed(2);
//                 const input6Element = document.getElementById("input6");
//                 input6Element.value = O2;
//                 let AO3 = (4238.7/(6.3979 - (Math.log(H20/100) / Math.log(10)))) - 460;
//                 // Dew //   
//                 let AP3 = ((AO3 - 32) / 1.8).toFixed(2);
//                 const input12Element = document.getElementById("input12");
//                 input12Element.value = AP3;
//             }
//             console.log('tempsecond:', temp.value);
//             document.getElementById("keyboardContainer").style.display = "none";
//         });
//     });
// });

// function updateSensorData() {
//     $.ajax({
//         type: 'GET',
//         url: '/get_sensor_values',
//         success: function(data) {
//             // Başarılı bir şekilde veri alındığında HTML içine yerleştir
//             $('#input1').val(data.co);
//             $('#input2').val(data.co2);
//             $('#input3').val(data.ch4);
//         },
//         error: function() {
//             console.error('Sensor data request failed.');
//         }
//     });
// }

// // Sayfa yüklendiğinde ve belirli aralıklarla sensör verilerini güncelle
// // (document).ready(function() {
// //     updateSensorData();
// //     setInterval(updateSensorData, 5000);  // 5 saniyede bir güncelleme yapılacak şekilde ayarlanmıştır
// // });

// $(function() {
//     updateSensorData();
//     setInterval(updateSensorData, 5000);  // 5 saniyede bir güncelleme yapılacak şekilde ayarlanmıştır
// });

// // Veriyi sunucuya gönderen yardımcı fonksiyon
// function sendToServer(dataToSend) {
//     // AJAX isteği ile Flask endpoint'ına gönder
//     fetch('/update_data', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(dataToSend),
//     })
//     .then(response => response.json())
//     .then(data => {
//         // İsteğin başarılı olması durumunda yapılacak işlemler
//         console.log(data);
//     })
//     .catch(error => {
//         // İstekte hata olması durumunda yapılacak işlemler
//         console.error('Error:', error);
//     });
// }

// function openKeyboard(inputId) {
//     // Klavye içeriğini keyboardContainer'a ekleyin
//     document.getElementById("keyboardContainer").innerHTML = `{% include 'numpad.html' %}`;
    
//     // Belirtilen input alanına değeri ekle
//     const inputField = document.getElementById(inputId);
//     const labelField = document.getElementById("numpadLabel"); // Yeni eklenen label
//     labelField.textContent = inputField.value;
//     let isLabelCleared = true;

//     // Her tuşa tıklandığında ilgili inputa değeri ekle
//     document.querySelectorAll('.numpad .key').forEach(key => {
//         key.addEventListener('click', function () {
//             const value = key.textContent;
//             key.classList.add("clicked");

//             if (inputField.value.charAt(0) === '0') {
//                 // Başında "0" varsa, "0" karakterini kaldır
//                 inputField.value = inputField.value.slice(1);
//             }

//             if(!(value =="Enter" || value =="Space"|| value =="Clear" || value =="X")){
//                 if (isLabelCleared) {
//                     inputField.value = '';
//                     labelField.textContent = ''; // Numpad label'ını temizle
//                     isLabelCleared = false; // Bayrağı sıfırla
//                 }
//                 inputField.value += value;  
//                 labelField.textContent += value;
//             }
//             setTimeout(function () {
//                 key.classList.remove("clicked");
//             }, 50);
                                        
//         });
        
//     });

//     // Space tuşuna basıldığında
//     // document.querySelector('.keyboard .space').addEventListener('click', function () {
//     //     document.getElementById(inputId).value += ' ';
//     // });

//     // Enter tuşuna basıldığında
//     document.querySelector('.numpad .close').addEventListener('click', function () {
//         // İsterseniz burada enter'a basıldığında yapılacak işlemleri ekleyebilirsiniz
//         // Örneğin bir form submit işlemi gibi
//         document.getElementById("keyboardContainer").style.display = "none";
//     });

//     // Enter tuşuna basıldığında
//     document.querySelector('.numpad .enter').addEventListener('click', function () {
//         // İsterseniz burada enter'a basıldığında yapılacak işlemleri ekleyebilirsiniz

//         const labelField = document.getElementById("numpadLabel"); 
//         const new_value = labelField.textContent;
//         const inputField = document.getElementById(inputId);
//         const input_id = inputField.name;

//         if (input_id && new_value) {
//             // AJAX isteği ile Flask endpoint'ını çağır
//             fetch('/update_data', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({
//                     input_id: input_id,  // Güncellenmesi istenen input alanının ID'si
//                     new_value: new_value,
//                 }),
//             })
//             .then(response => response.json())
//             .then(data => {
//                 // İsteğin başarılı olması durumunda yapılacak işlemler
//                 console.log(data);
//             })
//             .catch(error => {
//                 // İstekte hata olması durumunda yapılacak işlemler
//                 console.error('Error:', error);
//             });
//         } else {
//             console.error('Invalid inputIdchange.');
//         }
//         // Örneğin bir form submit işlemi gibi
//         document.getElementById("keyboardContainer").style.display = "none";
//         isLabelCleared = false;

//         // document.addEventListener('DOMContentLoaded', function() {
            
//         // });
//     });
    
//     // "Clear" tuşuna basıldığında yapılacak işlemler
//     document.querySelector('.numpad .clear').addEventListener('click', function () {
//         //const inputId = "input-field"; // Buradaki inputId değerini kendi kullanımınıza göre değiştirin
//         inputField.value = '0'; // Input alanını temizle
//         labelField.textContent = '0';
//         const new_value = labelField.textContent;
//         const input_id = inputField.value;

//         if (input_id && new_value) {
//             // AJAX isteği ile Flask endpoint'ını çağır
//             fetch('/update_data', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({
//                     input_id: input_id,  // Güncellenmesi istenen input alanının ID'si
//                     new_value: new_value,
//                 }),
//             })
//             .then(response => response.json())
//             .then(data => {
//                 // İsteğin başarılı olması durumunda yapılacak işlemler
//                 console.log(data);
//             })
//             .catch(error => {
//                 // İstekte hata olması durumunda yapılacak işlemler
//                 console.error('Error:', error);
//             });
//         } else {
//             console.error('Invalid inputIdchange.');
//         }
//     });

//     // Pop-up'ı görünür yap
//     document.getElementById("keyboardContainer").style.display = "block";
// }

// function closeKeyboard() {
//     // Pop-up'ı gizle
//     document.getElementById("keyboardContainer").style.display = "none";
// }

                    