# SpecialEquipmentID

AI-powered system for detecting and identifying special-purpose vehicles (e.g., 🚑 ambulance, 🚒 fire truck, 🚓 police car) based on images and metadata (EXIF, GPS, timestamp).

## 🎯 Опис

Ця інформаційна система створена в рамках дипломного проєкту та призначена для:
- автоматизованого розпізнавання спеціальної техніки;
- обробки супутніх метаданих (GPS, час, джерело зйомки);
- відображення результатів через вебінтерфейс;
- збереження історії аналізів для кожного користувача.

## 🛠️ Технології
- **FastAPI** — вебсервер та API
- **YOLOv8 OBB** — об’єктне розпізнавання (обертові прямокутники)
- **SQLite** — база даних
- **Jinja2** — шаблони HTML
- **CSS** — анімований стиль інтерфейсу

## 👥 Ролі користувачів
- **Адміністратор**
  - бачить усі аналізи
  - має доступ до статистики та графіків
  - керує користувачами (крім інших адмінів)
- **Користувач**
  - бачить лише свої завантаження
  - не бачить загальної статистики

## 📂 Запуск локально

```bash
# Клонування репозиторію
git clone https://github.com/your-username/SpecialEquipmentID.git
cd SpecialEquipmentID

# Запуск сервера
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
