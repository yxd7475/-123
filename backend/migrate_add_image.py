import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'warehouse.db')

if not os.path.exists(db_path):
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')

if os.path.exists(db_path):
    print(f"数据库路径: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(items)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'image' not in columns:
            cursor.execute("ALTER TABLE items ADD COLUMN image VARCHAR(255)")
            conn.commit()
            print("成功添加 image 字段到 items 表")
        else:
            print("image 字段已存在")
            
    except Exception as e:
        print(f"迁移失败: {e}")
    finally:
        conn.close()
else:
    print("数据库文件不存在")
