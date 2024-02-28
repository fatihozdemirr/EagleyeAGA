// Saati güncelleyen fonksiyon
function updateCurrentDatetime() {
    const currentDatetimeElement = document.getElementById('currentDatetime');
    if (currentDatetimeElement) {
        // Zamanı al
        const currentDatetime = new Date();
        
        // Zamanı belirli bir formata çevir (isteğe bağlı)
        const formattedDatetime = currentDatetime.toLocaleString(); // ya da başka bir format
        
        // HTML elementinin içeriğini güncelle
        currentDatetimeElement.textContent = formattedDatetime;
    }
}

// Saati belirli aralıklarla güncelleyen bir interval oluştur
setInterval(updateCurrentDatetime, 1000); // Her saniyede bir güncelle