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

            // เพิ่มไฟล์ที่อัพโหลดใหม่ไปยัง `uploadedFiles`
            Array.from(files).forEach(file => {
                uploadedFiles.push(file);
                displayImage(file);
            });

            // รีเซ็ต input เพื่อให้สามารถอัพโหลดไฟล์ใหม่ได้โดยไม่ต้องล้าง input
            uploadInput.value = '';
        });
    } else {
        console.error("Element with id 'upload-images' not found.");
    }

    // ฟังก์ชันสำหรับแสดงภาพที่อัพโหลด
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
            imgElement.style.width = '100px';
            imgElement.style.height = '100px';
            imgElement.style.objectFit = 'cover';
            imgElement.style.border = '1px solid #ddd';
            imgElement.style.borderRadius = '5px';

            // ปุ่มลบภาพ
            const removeButton = document.createElement('button');
            removeButton.innerHTML = 'x';
            removeButton.style.position = 'absolute';
            removeButton.style.top = '0';
            removeButton.style.right = '0';
            removeButton.style.backgroundColor = 'red';
            removeButton.style.color = 'white';
            removeButton.style.border = 'none';
            removeButton.style.borderRadius = '50%';
            removeButton.style.cursor = 'pointer';

            // เมื่อคลิกปุ่มลบ
            removeButton.addEventListener('click', function () {
                const index = Array.from(previewContainer.children).indexOf(imgWrapper);
                if (index > -1) {
                    uploadedFiles.splice(index, 1); // ลบไฟล์จาก `uploadedFiles`
                    previewContainer.removeChild(imgWrapper); // ลบ element ของภาพ
                }
            });

            // ใส่ img และปุ่มลบลงใน wrapper
            imgWrapper.appendChild(imgElement);
            imgWrapper.appendChild(removeButton);

            // เพิ่ม wrapper ลงใน previewContainer
            previewContainer.appendChild(imgWrapper);
        };

        reader.onerror = function () {
            console.error('Error reading file', file);
            alert('Error loading file: ' + file.name);
        };

        if (file) {
            reader.readAsDataURL(file); // อ่านไฟล์และแสดงผลเป็น Base64
        }
    }
});
