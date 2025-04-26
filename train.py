import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from ultralytics import YOLO

# 1. Параметри
DATA_DIR = '/Users/vlodochka1/Desktop/MilitaryDetect.v1i.yolov8-obb'
PLOTS_DIR = 'plots'
os.makedirs(PLOTS_DIR, exist_ok=True)

TRAIN_DIR = os.path.join(DATA_DIR, 'train', 'images')
VAL_DIR = os.path.join(DATA_DIR, 'valid', 'images')
TEST_DIR = os.path.join(DATA_DIR, 'test', 'images')

CONFIG_FILE = 'obb_config.yaml'
MODEL_NAME = 'yolov8n-obb.pt'

EPOCHS = 30
IMG_SIZE = 640
BATCH_SIZE = 32

# 2. Перевірка папок і даних
for dir_path in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"❌ Папка не знайдена: {dir_path}")
    else:
        print(f"✅ Папка знайдена: {dir_path} ({len(os.listdir(dir_path))} файлів)")

# 3. Створення YAML для навчання
data_yaml = f"""
path: {os.path.abspath(DATA_DIR)}
train: train/images
val: valid/images
test: test/images
nc: 5
names: ['helicopter', 'jet', 'sam', 'tank', 'truck']
"""
with open(CONFIG_FILE, 'w') as f:
    f.write(data_yaml)

print(f"📄 YAML файл збережено: {CONFIG_FILE}")

# 4. Навчання моделі YOLOv8 OBB
model = YOLO(MODEL_NAME)

results = model.train(
    data=CONFIG_FILE,
    imgsz=IMG_SIZE,
    epochs=EPOCHS,
    batch=BATCH_SIZE,
    patience=10,
    workers=4,
    optimizer='SGD',
    cos_lr=True,
    verbose=True
)

# 5. Збереження історії втрат
history = {
    'train_loss': results.metrics.box_loss,
    'val_loss': results.metrics.val_box_loss,
    'precision': results.metrics.precision,
    'recall': results.metrics.recall,
    'map50': results.metrics.map50,
    'map50_95': results.metrics.map
}

history_df = pd.DataFrame([history])
history_df.to_csv(os.path.join(PLOTS_DIR, 'training_history.csv'), index=False)
print("✅ Історію навчання збережено у training_history.csv")

# 6. Графік втрат
plt.figure(figsize=(10,6))
if hasattr(results, 'losses') and 'box' in results.losses:
    plt.plot(results.losses['box'], label='train_box_loss')
else:
    print("⚠️ Warning: Немає збережених значень losses['box'] для побудови графіку.")

plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Box Loss Curve')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(PLOTS_DIR, 'box_loss_curve.png'))
plt.close()
print("✅ Графік втрат збережено у box_loss_curve.png")

# 7. Показати результати тренування
results_dir = model.save_dir
metrics_path = os.path.join(results_dir, 'results.png')
if os.path.exists(metrics_path):
    img = plt.imread(metrics_path)
    plt.figure(figsize=(12,8))
    plt.imshow(img)
    plt.axis('off')
    plt.title('Training Results')
    plt.show()
else:
    print("⚠️ Warning: results.png не знайдено для візуалізації.")

print("🎯 Навчання завершено успішно!")
