import os
from ultralytics import YOLO
import pandas as pd
import matplotlib.pyplot as plt

# Константи
DATA_DIR = '/Users/vlodochka1/Special_Equipment.v1i.yolov8'
PLOTS_DIR = 'plots'
CONFIG_FILE = 'config.yaml'
EPOCHS = 10
IMG_SIZE = 640
BATCH_SIZE = 32
PRETRAINED_MODEL = '/Users/vlodochka1/runs/detect/train4/weights/best.pt'  

# Створення папки для графіків
os.makedirs(PLOTS_DIR, exist_ok=True)

# Генерація YAML
yaml_content = f"""path: {os.path.abspath(DATA_DIR)}
train: train/images
val: valid/images
test: test/images
nc: 5
names: ['ambulance', 'fire engine', 'gas emergency', 'police car', 'rescue helicopter']
"""
with open(CONFIG_FILE, 'w') as f:
    f.write(yaml_content)
print(f"📄 YAML файл збережено: {CONFIG_FILE}")

# Завантаження моделі
model = YOLO(PRETRAINED_MODEL)

# Донавчання
results = model.train(
    data=CONFIG_FILE,
    imgsz=IMG_SIZE,
    epochs=EPOCHS,
    batch=BATCH_SIZE,
    patience=10,
    workers=4,
    optimizer='SGD',
    lr0=0.001,
    cos_lr=True,
    verbose=True
)

# Побудова графіку втрат
plt.figure(figsize=(10, 6))
try:
    if hasattr(results, 'losses') and 'box' in results.losses:
        plt.plot(results.losses['box'], label='train_box_loss')
except Exception as e:
    print("⚠️ Немає доступних даних по втратам:", e)

plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Finetuning Box Loss')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(PLOTS_DIR, 'finetune_box_loss_curve.png'))
plt.close()
print("✅ Збережено графік втрат після донавчання")
