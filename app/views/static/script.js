const loaderOverlay = document.getElementById('loader-overlay');
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const preview = document.getElementById('preview');
const submitBtn = document.getElementById('submit-btn');
const progressBar = document.getElementById('progress-bar');
const progressContainer = document.querySelector('.progress-container');

// Обробка вибору файлу
uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFiles);

function handleFiles(e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(event) {
            preview.src = event.target.result;
            preview.style.display = 'block';
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

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerText = message;

    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

submitBtn.addEventListener('click', async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
        showNotification('Помилка: файл не обрано!', 'error');
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
                showNotification(`Помилка: ${data.error}`, 'error');
            } else {
                showNotification('Успішно завантажено!', 'success');
                setTimeout(() => {
                    window.location.href = `/result?class=${encodeURIComponent(data.class)}&confidence=${encodeURIComponent(data.confidence)}`;
                }, 1000);
            }
        } else {
            showNotification('Помилка: Сервер повернув некоректну відповідь.', 'error');
        }

    } catch (error) {
        console.error('Помилка:', error);
        showNotification('Помилка при обробці запиту!', 'error');
    } finally {
        hideLoader();
    }
});

// Прогрес бар
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
