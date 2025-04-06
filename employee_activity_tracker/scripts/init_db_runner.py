import pymysql
import os

# 读取 SQL 文件
with open("scripts/init_db.sql", "r") as f:
    sql = f.read()

# 连接数据库
conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "employee_tracking"),
)

cursor = conn.cursor()
for statement in sql.split(";"):
    if statement.strip():
        cursor.execute(statement)

conn.commit()
conn.close()

print("✅ Database initialized successfully.")
