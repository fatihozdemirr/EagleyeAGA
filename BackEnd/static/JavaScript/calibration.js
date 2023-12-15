// document.addEventListener('DOMContentLoaded', function() {
//     document.querySelectorAll('.span-button').forEach(button => {
//         button.addEventListener('click', function() {
//             const action = this.getAttribute('data-action');
//             console.log(`Performing action: ${action}`);
//         });
//     });

//     // Sayfa yüklendikten sonra input elementine click olayını dinle
//     var inputElement = document.getElementById('inputoffset');
//     if (inputElement) {
//         inputElement.addEventListener('click', function() {
//             openNumpad('inputoffset');
//             document.getElementById("keyboardContainer").style.display = "none";
//         });
//     }
//     else {
//         console.error("Input element with ID 'inputoffset' not found.");
//     }
// });

// function openNumpad(inputId) {
//     // alert("Numpad açılıyor: " + inputId);
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
//     document.querySelector('.numpad .close').addEventListener('click', function () {
//         // İsterseniz burada enter'a basıldığında yapılacak işlemleri ekleyebilirsiniz
//         // Örneğin bir form submit işlemi gibi
//         document.getElementById("keyboardContainer").style.display = "none";
//     });

//     // Enter tuşuna basıldığında
//     document.querySelector('.numpad .enter').addEventListener('click', function () {
//         document.getElementById("keyboardContainer").style.display = "none";
//         isLabelCleared = false;
//     });
//     // "Clear" tuşuna basıldığında yapılacak işlemler
//     document.querySelector('.numpad .clear').addEventListener('click', function () {
//         //const inputId = "input-field"; // Buradaki inputId değerini kendi kullanımınıza göre değiştirin
//         inputField.value = '0'; // Input alanını temizle
//         labelField.textContent = '0';
//     });
//     // Pop-up'ı görünür yap
//     document.getElementById("keyboardContainer").style.display = "block";
// }
// function closeKeyboard() {
//     // Pop-up'ı gizle
//     document.getElementById("keyboardContainer").style.display = "none";
// }
