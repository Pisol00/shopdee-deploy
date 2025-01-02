document.addEventListener('DOMContentLoaded', function () {
    // Handle size selection
    const sizeOptions = document.querySelectorAll('.size-option');
    const purchaseOptions = document.getElementById('purchase-options');

    sizeOptions.forEach(option => {
        option.addEventListener('click', function () {
            sizeOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            purchaseOptions.style.display = 'block';
        });
    });

    // Handle purchase option selection
    const buyButtons = document.querySelectorAll('.buy-button');
    buyButtons.forEach(button => {
        button.addEventListener('click', function () {
            const condition = this.getAttribute('data-condition');
            const selectedSize = document.querySelector('.size-option.active').getAttribute('data-size');
            const collectionId = this.getAttribute('data-collection-id'); // ดึง collection_id
            window.location.href = `/product_checkout/?condition=${condition}&size=${selectedSize}&collection_id=${collectionId}`; // เพิ่ม collection_id ใน URL
        });
    });

    // Handle sell button selection
    const sellButton = document.querySelector('.sell-button');
    if (sellButton) {
        sellButton.addEventListener('click', function () {
            const selectedSize = document.querySelector('.size-option.active') ? document.querySelector('.size-option.active').getAttribute('data-size') : ''; // ดึง selected size
            const collectionId = this.getAttribute('data-collection-id'); // ดึง collection_id
            window.location.href = `/sell_detail/?action=sell&collection_id=${collectionId}&size=${selectedSize}`; // ส่งค่า collection_id และ size ไปที่ URL
        });
    }
});