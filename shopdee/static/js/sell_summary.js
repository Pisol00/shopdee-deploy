document.addEventListener('DOMContentLoaded', function () {
    const uploadInput = document.getElementById('upload-images');
    const previewContainer = document.getElementById('preview-images');
    let uploadedFiles = []; // เก็บไฟล์ที่อัพโหลด

    if (uploadInput) {
        uploadInput.addEventListener('change', function (event) {
            const files = event.target.files;

            if (files.length === 0) {
                alert('No files selected');
                return;
            }

            Array.from(files).forEach(file => {
                uploadedFiles.push(file);
                displayImage(file);
            });

            uploadInput.value = ''; // รีเซ็ต input
        });
    }

    function displayImage(file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            const imgWrapper = document.createElement('div');
            imgWrapper.classList.add('image-wrapper');
            imgWrapper.style.position = 'relative';
            imgWrapper.style.display = 'inline-block';
            imgWrapper.style.margin = '10px';

            const imgElement = document.createElement('img');
            imgElement.src = e.target.result;
            imgElement.classList.add('preview-image');

            const removeButton = document.createElement('button');
            removeButton.innerHTML = 'x';
            removeButton.classList.add('remove-button');

            removeButton.addEventListener('click', function () {
                const index = Array.from(previewContainer.children).indexOf(imgWrapper);
                if (index > -1) {
                    uploadedFiles.splice(index, 1);
                    previewContainer.removeChild(imgWrapper);
                }
            });

            imgWrapper.appendChild(imgElement);
            imgWrapper.appendChild(removeButton);
            previewContainer.appendChild(imgWrapper);
        };

        reader.onerror = function () {
            console.error('Error reading file', file);
            alert('Error loading file: ' + file.name);
        };

        if (file) {
            reader.readAsDataURL(file);
        }
    }
});
