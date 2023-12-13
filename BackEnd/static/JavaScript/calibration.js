document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.span-button').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            // action'a bağlı olarak belirli işlemleri gerçekleştir
            console.log(`Performing action: ${action}`);
            // ... diğer işlemler
        });
    });
});