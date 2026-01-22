import sqlite3
import json
import glob
import os
import time

# 定义数据库路径
DB_PATH = "creds/credentials.db"
CREDS_DIR = "creds"

def import_json_to_sqlite():
    # 1. 确保目录存在
    if not os.path.exists(CREDS_DIR):
        os.makedirs(CREDS_DIR)

    # 2. 连接数据库 (如果不存在会自动创建)
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 3. 确保表存在 (复制自源码的建表逻辑，防止脚本先于主程序运行报错)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            credential_data TEXT NOT NULL,
            disabled INTEGER DEFAULT 0,
            error_codes TEXT DEFAULT '[]',
            last_success REAL,
            user_email TEXT,
            model_cooldowns TEXT DEFAULT '{}',
            rotation_order INTEGER DEFAULT 0,
            call_count INTEGER DEFAULT 0,
            created_at REAL DEFAULT (unixepoch()),
            updated_at REAL DEFAULT (unixepoch())
        )
    """)

    # 4. 扫描所有 JSON 文件
    json_files = glob.glob(os.path.join(CREDS_DIR, "*.json"))
    print(f"Found {len(json_files)} JSON files in {CREDS_DIR}")

    count = 0
    for file_path in json_files:
        try:
            filename = os.path.basename(file_path)
            
            # 读取 JSON 内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 验证一下是不是合法的 JSON
                json_data = json.loads(content)
            
            # 5. 插入或更新到数据库
            # 使用 INSERT OR REPLACE，这样如果你在 Render 更新了 JSON，重启后数据库也会更新
            cursor.execute("""
                INSERT OR REPLACE INTO credentials 
                (filename, credential_data, updated_at, created_at)
                VALUES (?, ?, ?, ?)
            """, (filename, content, time.time(), time.time()))
            
            print(f"Imported: {filename}")
            count += 1
            
        except Exception as e:
            print(f"Error importing {file_path}: {e}")

    # 6. 提交更改并关闭
    conn.commit()
    conn.close()
    print(f"Successfully imported {count} credentials.")

if __name__ == "__main__":
    import_json_to_sqlite()
