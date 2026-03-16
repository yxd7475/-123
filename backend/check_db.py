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
        cursor.execute("PRAGMA table_info(inbound_records)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"inbound_records 列: {columns}")
        
        cursor.execute("PRAGMA table_info(outbound_records)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"outbound_records 列: {columns}")
        
        print("数据库结构检查完成")
            
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        conn.close()
else:
    print("数据库文件不存在")
