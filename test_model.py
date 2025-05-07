import os
from ultralytics import YOLO

# Завантажуємо модель
model = YOLO("app/models/military_detect_best.pt")

# Шлях до папки з тестовими зображеннями
images_dir = '/Users/vlodochka1/Desktop/MilitaryDetect.v1i.yolov8-obb/test/images'

# Створюємо окрему папку для збереження результатів, якщо потрібно
save_dir = 'runs/predict_all'
os.makedirs(save_dir, exist_ok=True)

# Перебираємо всі зображення у папці
for img_name in os.listdir(images_dir):
    if img_name.endswith(('.jpg', '.jpeg', '.png')):  # тільки картинки
        img_path = os.path.join(images_dir, img_name)
        
        # Робимо передбачення і зберігаємо результат
        results = model.predict(
            source=img_path,
            save=True,
            save_dir=save_dir,
            imgsz=640,
            verbose=False
        )

print("✅ Усі передбачення завершено!")
print(f"Результати збережено в папці: {save_dir}")
