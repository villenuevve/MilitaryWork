const loaderOverlay = document.getElementById('loader-overlay');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewImage = document.getElementById('preview-image');
const fileName = document.getElementById('file-name');
const previewContainer = document.getElementById('preview-container');
const submitBtn = document.getElementById('submit-btn');
const progressBar = document.getElementById('progress-bar');
const progressContainer = document.querySelector('.progress-container');

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragging');
});
dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragging');
});
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragging');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        showPreview(files[0]);
    }
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        showPreview(fileInput.files[0]);
    }
});

function showPreview(file) {
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(event) {
            previewImage.src = event.target.result;
            previewImage.style.display = 'block';
            previewContainer.style.display = 'block';
            fileName.textContent = `✅ Обрано файл: ${file.name}`;
        };
        reader.readAsDataURL(file);
    }
}

function showLoader() {
    loaderOverlay.classList.add('visible');
    startFakeProgress();
}
function hideLoader() {
    loaderOverlay.classList.remove('visible');
    finishProgress();
}

submitBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) {
        alert('Файл не обрано!');
        return;
    }
    showLoader();
    const formData = new FormData();
    formData.append('image', file);
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData,
        });
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            const data = await response.json();
            if (data.error) {
                alert(`Помилка: ${data.error}`);
            } else {
                window.location.href = `/result?class=${encodeURIComponent(data.class)}&confidence=${encodeURIComponent(data.confidence)}`;
            }
        } else {
            alert('Некоректна відповідь сервера.');
        }
    } catch (error) {
        console.error('Помилка:', error);
        alert('Помилка при обробці запиту!');
    } finally {
        hideLoader();
    }
});

function startFakeProgress() {
    progressContainer.style.display = 'block';
    let width = 0;
    const interval = setInterval(() => {
        if (width >= 90) {
            clearInterval(interval);
        } else {
            width += Math.random() * 2;
            progressBar.style.width = width + '%';
        }
    }, 150);
}
function finishProgress() {
    progressBar.style.width = '100%';
    setTimeout(() => {
        progressContainer.style.display = 'none';
        progressBar.style.width = '0%';
    }, 500);
}