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
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS inbound_records_new (
                id INTEGER PRIMARY KEY,
                record_no VARCHAR(50) UNIQUE NOT NULL,
                item_id INTEGER NOT NULL,
                item_code VARCHAR(50) NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                inbound_type VARCHAR(20) NOT NULL,
                quantity FLOAT NOT NULL,
                unit_price FLOAT NOT NULL DEFAULT 0,
                total_price FLOAT NOT NULL DEFAULT 0,
                source VARCHAR(100),
                supplier VARCHAR(100),
                handler VARCHAR(50),
                operator_id INTEGER,
                remark TEXT,
                status VARCHAR(20) DEFAULT 'completed',
                created_at DATETIME,
                FOREIGN KEY(item_id) REFERENCES items (id),
                FOREIGN KEY(operator_id) REFERENCES users (id)
            );
            
            INSERT INTO inbound_records_new SELECT * FROM inbound_records;
            DROP TABLE inbound_records;
            ALTER TABLE inbound_records_new RENAME TO inbound_records;
            
            CREATE TABLE IF NOT EXISTS outbound_records_new (
                id INTEGER PRIMARY KEY,
                record_no VARCHAR(50) UNIQUE NOT NULL,
                item_id INTEGER NOT NULL,
                item_code VARCHAR(50) NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                outbound_type VARCHAR(20) NOT NULL,
                quantity FLOAT NOT NULL,
                unit_price FLOAT NOT NULL DEFAULT 0,
                total_price FLOAT NOT NULL DEFAULT 0,
                destination VARCHAR(100),
                receiver VARCHAR(50),
                handler VARCHAR(50),
                operator_id INTEGER,
                remark TEXT,
                status VARCHAR(20) DEFAULT 'completed',
                created_at DATETIME,
                FOREIGN KEY(item_id) REFERENCES items (id),
                FOREIGN KEY(operator_id) REFERENCES users (id)
            );
            
            INSERT INTO outbound_records_new SELECT * FROM outbound_records;
            DROP TABLE outbound_records;
            ALTER TABLE outbound_records_new RENAME TO outbound_records;
        """)
        conn.commit()
        print("数据库迁移成功")
            
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()
else:
    print("数据库文件不存在")
