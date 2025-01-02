document.addEventListener("DOMContentLoaded", function () {
  // Handle size selection
  const sizeOptions = document.querySelectorAll(".size-option");
  const purchaseOptions = document.getElementById("purchase-options");

  sizeOptions.forEach((option) => {
    option.addEventListener("click", function () {
      sizeOptions.forEach((opt) => opt.classList.remove("active"));
      this.classList.add("active");
      purchaseOptions.style.display = "block";
    });
  });

  // Handle purchase option selection
  const buyButtons = document.querySelectorAll(".buy-button");
  buyButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const condition = this.getAttribute("data-condition");
      const selectedSize = document.querySelector(".size-option.active").getAttribute("data-size");
      const collectionId = this.getAttribute("data-collection-id");
      const category = this.getAttribute("data-category");

      if (condition === "used") {
        window.location.href = `/show-product-by-condition/?size=${selectedSize}&collection_id=${collectionId}&category=${category}&condition=${condition}`;
      } else if (condition === "brand_new") {
        window.location.href = `/show-product-by-condition/?size=${selectedSize}&collection_id=${collectionId}&category=${category}&condition=${condition}`;
      }
    });
  });

  // Handle sell button selection
  const sellButton = document.querySelector(".sell-button");
  if (sellButton) {
    sellButton.addEventListener("click", function () {
      const selectedSize = document.querySelector(".size-option.active")
        ? document.querySelector(".size-option.active").getAttribute("data-size")
        : "";
      const collectionId = this.getAttribute("data-collection-id");
      window.location.href = `/sell_detail/?action=sell&collection_id=${collectionId}&size=${selectedSize}`;
    });
  }
});
