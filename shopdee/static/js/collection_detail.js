document.addEventListener('DOMContentLoaded', function () {
    const productContainerNewArrivals = document.getElementById('productContainerNewArrivals');
    const nextBtnNewArrivals = document.getElementById('nextBtnNewArrivals');
    const prevBtnNewArrivals = document.getElementById('prevBtnNewArrivals');

    const productContainerTopSelling = document.getElementById('productContainerTopSelling');
    const nextBtnTopSelling = document.getElementById('nextBtnTopSelling');
    const prevBtnTopSelling = document.getElementById('prevBtnTopSelling');

    const scrollStep = 200;

    nextBtnNewArrivals.addEventListener('click', () => {
        productContainerNewArrivals.scrollLeft += scrollStep;
    });

    prevBtnNewArrivals.addEventListener('click', () => {
        productContainerNewArrivals.scrollLeft -= scrollStep;
    });

    nextBtnTopSelling.addEventListener('click', () => {
        productContainerTopSelling.scrollLeft += scrollStep;
    });

    prevBtnTopSelling.addEventListener('click', () => {
        productContainerTopSelling.scrollLeft -= scrollStep;
    });
});

function changeMainImage(imageUrl) {
    const mainImage = document.getElementById('mainImage');
    mainImage.src = imageUrl;
}

// Add onclick event to each thumbnail
document.querySelectorAll('.thumbnail').forEach(thumbnail => {
    thumbnail.addEventListener('click', function () {
        const imageUrl = this.querySelector('img').src;
        changeMainImage(imageUrl);
    });
});
