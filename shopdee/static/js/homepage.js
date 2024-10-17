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