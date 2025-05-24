import json
import sqlite3
import ast

def fix_meta_info_format():
    conn = sqlite3.connect("app/models/detections.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, meta_info FROM detection")
    rows = cursor.fetchall()

    updated = 0

    for row in rows:
        det_id, meta_info_raw = row

        if not meta_info_raw:
            continue

        try:
            #декодувати як JSON 
            json.loads(meta_info_raw)
        except json.JSONDecodeError:
            try:
                #конвертувати з Python str до словника
                fixed_dict = ast.literal_eval(meta_info_raw)

                if isinstance(fixed_dict, dict):
                    fixed_json = json.dumps(fixed_dict)
                    cursor.execute(
                        "UPDATE detection SET meta_info = ? WHERE id = ?",
                        (fixed_json, det_id)
                    )
                    updated += 1
            except Exception as e:
                print(f"[!] Неможливо виправити meta_info для id={det_id}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Виправлено {updated} записів.")

if __name__ == "__main__":
    fix_meta_info_format()
