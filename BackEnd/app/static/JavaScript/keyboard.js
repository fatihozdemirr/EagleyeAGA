var shiftPressed = false;

// Shift tuşuna basıldığında veya serbest bırakıldığında bu fonksiyonu çağırın
function handleShiftKey(event) {
    // Klavye olayının Shift tuşuna basıldığını veya serbest bırakıldığını kontrol edin
    if (event.key === "Shift") {
        // Shift tuşunun durumunu güncelleyin
        shiftPressed = event.type === "keydown";
    }
}

// Klavye olaylarını dinleyin
document.addEventListener("keydown", handleShiftKey);
document.addEventListener("keyup", handleShiftKey);

// Klavye tuşlarının tıklanma işlevini belirleyin
document.querySelectorAll(".key").forEach(function(key) {
    key.addEventListener("click", function() {
        // Tuşun içeriğini alın
        var keyContent = key.textContent;
        
        // Eğer Shift tuşu basılıysa ve tuş bir harf ise büyük/küçük harf dönüşümü yapın
        if (shiftPressed && keyContent.length === 1 && /[a-zA-Z]/.test(keyContent)) {
            // Harfi büyük harfe veya küçük harfe dönüştürün
            key.textContent = keyContent.toUpperCase() === keyContent ? keyContent.toLowerCase() : keyContent.toUpperCase();
        }
    });
});