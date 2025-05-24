import os

DATA_DIR = '/Users/vlodochka1/Special_Equipment.v1i.yolov8-obb'
SUBSETS = ['train', 'valid', 'test']
EXPECTED_COLS = 6

def check_label_format(label_file):
    with open(label_file, 'r') as f:
        for i, line in enumerate(f.readlines(), 1):
            parts = line.strip().split()
            if len(parts) != EXPECTED_COLS:
                return f"{label_file} (рядок {i} — {len(parts)} колонок)"
    return None

bad_labels = []
for subset in SUBSETS:
    label_dir = os.path.join(DATA_DIR, subset, 'labels')
    for file in os.listdir(label_dir):
        if file.endswith('.txt'):
            full_path = os.path.join(label_dir, file)
            result = check_label_format(full_path)
            if result:
                bad_labels.append(result)

print("❌ Проблемні анотації:")
for item in bad_labels:
    print("-", item)

print(f"\n🔍 Всього файлів з проблемами: {len(bad_labels)}")
