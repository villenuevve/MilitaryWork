const loaderOverlay = document.getElementById('loader-overlay');
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const preview = document.getElementById('preview');
const submitBtn = document.getElementById('submit-btn');

uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFiles);

function handleFiles(e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(event) {
            preview.src = event.target.result;
            preview.style.display = 'block';
        }
        reader.readAsDataURL(file);
    }
}

// Показати / сховати лоадер
function showLoader() {
    loaderOverlay.classList.add('visible');
}

function hideLoader() {
    loaderOverlay.classList.remove('visible');
}

// Сповіщення
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerText = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// Відправка файлу
submitBtn.addEventListener('click', async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
        showNotification('Помилка: файл не обрано!', 'error');
        return;
    }

    // Показати лоадер
    showLoader();

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Помилка сервера');
        }

        const data = await response.json();

        if (data.error) {
            showNotification(`Помилка: ${data.error}`, 'error');
        } else {
            showNotification('Успішно завантажено!', 'success');
            // Через 1 секунду після повідомлення перейти на results
            setTimeout(() => {
                window.location.href = `/result?class=${data.class}&confidence=${data.confidence}&angle=${data.angle}`;
            }, 1000);
        }

    } catch (error) {
        console.error('Помилка:', error);
        showNotification('Помилка обробки!', 'error');
    } finally {
        hideLoader();
        finishProgress(); 
    }
});

const progressBar = document.getElementById('progress-bar');
const progressContainer = document.querySelector('.progress-container');

function startFakeProgress() {
    progressContainer.style.display = 'block';
    let width = 0;

    const interval = setInterval(() => {
        if (width >= 90) { // Залишимо трохи простору для реального завершення
            clearInterval(interval);
        } else {
            width += Math.random() * 2; // Рандомно +1..2% для реалістичності
            progressBar.style.width = width + '%';
        }
    }, 200); // Кожні 200мс
}

function finishProgress() {
    progressBar.style.width = '100%';
    setTimeout(() => {
        progressContainer.style.display = 'none';
        progressBar.style.width = '0%'; // Скинути для наступного разу
    }, 500); // Після короткої затримки
}
