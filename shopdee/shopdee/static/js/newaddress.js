document.addEventListener("DOMContentLoaded", function () {
    const provinceSelect = document.getElementById("province");
    const districtSelect = document.getElementById("district");
    const subdistrictSelect = document.getElementById("subdistrict");
    const postalCodeInput = document.getElementById("postal_code");

    // Hidden fields for names
    const provinceNameInput = document.getElementById("province_name");
    const districtNameInput = document.getElementById("district_name");
    const subdistrictNameInput = document.getElementById("subdistrict_name");

    provinceSelect.addEventListener("change", function () {
        const provinceId = this.value;
        const provinceName = this.options[this.selectedIndex].textContent;
        provinceNameInput.value = provinceName; // Set province name in hidden field

        // Clear existing options
        districtSelect.innerHTML = '<option value="">Select District</option>';
        subdistrictSelect.innerHTML = '<option value="">Select Subdistrict</option>';

        if (provinceId) {
            // Fetch districts based on province selection
            fetch(`/get_districts/${provinceId}/`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then((data) => {
                    data.districts.forEach(function (district) {
                        const option = document.createElement("option");
                        option.value = district.id;
                        option.textContent = district.name_en;
                        districtSelect.appendChild(option);
                    });
                })
                .catch((error) => console.error("Fetch Error:", error));
        }
    });

    districtSelect.addEventListener("change", function () {
        const districtId = this.value;
        const districtName = this.options[this.selectedIndex].textContent;
        districtNameInput.value = districtName; // Set district name in hidden field

        // Clear existing subdistrict options
        subdistrictSelect.innerHTML = '<option value="">Select Subdistrict</option>';

        if (districtId) {
            // Fetch subdistricts based on district selection
            fetch(`/get_subdistricts/${districtId}/`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then((data) => {
                    data.subdistricts.forEach(function (subdistrict) {
                        const option = document.createElement("option");
                        option.value = subdistrict.id;
                        option.textContent = subdistrict.name_en;
                        subdistrictSelect.appendChild(option);
                    });
                })
                .catch((error) => console.error("Fetch Error:", error));
        }
    });

    subdistrictSelect.addEventListener("change", function () {
        const subdistrictId = this.value;
        const subdistrictName = this.options[this.selectedIndex].textContent;
        subdistrictNameInput.value = subdistrictName; // Set subdistrict name in hidden field

        if (subdistrictId) {
            // Fetch postal code based on subdistrict selection
            fetch(`/get_subdistricts/${districtSelect.value}/`)
                .then((response) => response.json())
                .then((data) => {
                    const selectedSubdistrict = data.subdistricts.find(
                        (subdistrict) => subdistrict.id == subdistrictId
                    );
                    if (selectedSubdistrict) {
                        postalCodeInput.value = selectedSubdistrict.postal_code;
                    }
                })
                .catch((error) => console.error("Fetch Error:", error));
        } else {
            postalCodeInput.value = "";
        }
    });
});
