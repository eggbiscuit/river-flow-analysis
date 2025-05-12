import sqlite3
import os

def initialize_database():
    # 获取当前脚本的绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "../db/river_network.db")
    schema_path = os.path.join(base_dir, "../sql/init_schema.sql")

    # 确保 db 目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 初始化表结构
    with open(schema_path, "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("✅ 数据库初始化成功")

if __name__ == "__main__":
    initialize_database()