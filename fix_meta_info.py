import json
import sqlite3
import ast

def fix_meta_info_format():
    conn = sqlite3.connect("app/models/detections.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, meta_info FROM detection")
    rows = cursor.fetchall()

    updated = 0

    for det_id, meta_info_raw in rows:
        if not meta_info_raw:
            continue

        # Перевірка, чи вже валідний JSON
        try:
            json.loads(meta_info_raw)
            continue 
        except json.JSONDecodeError:
            pass  

        try:
            fixed_dict = ast.literal_eval(meta_info_raw)

            if isinstance(fixed_dict, dict):
                fixed_json = json.dumps(fixed_dict, ensure_ascii=False)
                cursor.execute(
                    "UPDATE detection SET meta_info = ? WHERE id = ?",
                    (fixed_json, det_id)
                )
                updated += 1
                print(f"🔧 Виправлено ID {det_id}")
            else:
                print(f"[!] ID={det_id} → не словник: {type(fixed_dict)}")

        except Exception as e:
            print(f"[!] Неможливо виправити ID={det_id}: {e}")

    conn.commit()
    conn.close()
    print(f"\n✅ Загалом виправлено {updated} записів.")

if __name__ == "__main__":
    fix_meta_info_format()