document.addEventListener("DOMContentLoaded", () => {
    const loaderOverlay = document.getElementById("loader-overlay");
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const previewImage = document.getElementById("preview-image");
    const fileName = document.getElementById("file-name");
    const previewContainer = document.getElementById("preview-container");
    const uploadForm = document.getElementById("upload-form");
    const progressBar = document.getElementById("progress-bar");
    const progressContainer = document.querySelector(".progress-container");
    const passwordInput = document.getElementById("password");
    const togglePassword = document.getElementById("toggle-password");

    if (dropZone && fileInput) {
        dropZone.addEventListener("click", () => fileInput.click());

        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragging");
        });

        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("dragging");
        });

        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragging");
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                showPreview(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                showPreview(fileInput.files[0]);
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener("submit", (e) => {
            const file = fileInput?.files[0];
            if (!file) {
                e.preventDefault();
                alert("Файл не обрано!");
                return;
            }
            showLoader();
        });
    }

    const togglePasswordIcons = document.querySelectorAll(".toggle-password");
    togglePasswordIcons.forEach((icon) => {
        icon.addEventListener("click", () => {
            const passwordInput = icon.previousElementSibling;
            if (passwordInput && passwordInput.type === "password") {
                passwordInput.type = "text";
                icon.textContent = "🙈";
            } else if (passwordInput) {
                passwordInput.type = "password";
                icon.textContent = "👁";
            }
        });
    });

    function showPreview(file) {
        if (file && file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImage.src = e.target.result;
                previewImage.style.display = "block";
                previewContainer.style.display = "block";
                fileName.textContent = `✅ Обрано файл: ${file.name}`;
            };
            reader.readAsDataURL(file);
        }
    }

    function showLoader() {
        loaderOverlay?.classList.add("visible");
        startFakeProgress();
    }

    function hideLoader() {
        loaderOverlay?.classList.remove("visible");
        finishProgress();
    }

    function startFakeProgress() {
        if (!progressContainer || !progressBar) return;
        progressContainer.style.display = "block";
        let width = 0;
        const interval = setInterval(() => {
            if (width >= 90) {
                clearInterval(interval);
            } else {
                width += Math.random() * 3;
                progressBar.style.width = width + "%";
            }
        }, 120);
    }

    function finishProgress() {
        if (!progressContainer || !progressBar) return;
        progressBar.style.width = "100%";
        setTimeout(() => {
            progressContainer.style.display = "none";
            progressBar.style.width = "0%";
        }, 600);
    }

    document.querySelectorAll("th.sortable").forEach(header => {
        header.addEventListener("click", () => {
            const table = header.closest("table");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));
            const index = Array.from(header.parentNode.children).indexOf(header);
            const isAsc = header.classList.toggle("asc");
    
            rows.sort((a, b) => {
                const valA = a.children[index].textContent.trim();
                const valB = b.children[index].textContent.trim();
                return isAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            });
    
            rows.forEach(row => tbody.appendChild(row));
        });
    });    
});