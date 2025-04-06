import pymysql
import pymysql
import random
from faker import Faker
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# 在populate_data.py顶部添加
import os
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"  # 自动定位.env
load_dotenv(env_path)


# 初始化
fake = Faker()
load_dotenv()  # 加载环境变量

# # 数据库配置
# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": os.getenv(
#         "MYSQL_PASSWORD"
#     ),  # 在.env文件中设置MYSQL_PASSWORD=yourpassword
#     "database": "employee_tracking",
#     "charset": "utf8mb4",
#     "cursorclass": pymysql.cursors.DictCursor,
# }

# 更新DB_CONFIG
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql"),  # 使用docker服务名
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "database": os.getenv("DB_NAME", "employee_tracking"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


# 部门与职位配置
departments = ["Sales", "Marketing", "IT", "Finance", "Product"]
job_titles = {
    "Sales": ["Sales Rep", "Account Manager", "Sales Director"],
    "Marketing": ["Content Specialist", "SEO Analyst", "Marketing Manager"],
    "IT": ["Developer", "SysAdmin", "Data Engineer"],
    "Finance": ["Accountant", "Financial Analyst", "CFO"],
    "Product": ["Product Manager", "UX Designer", "Researcher"],
}

# 活动描述模板
activity_templates = {
    "Sales": [
        "Met with {n} clients",
        "Prepared Q{quarter} sales report",
        "Attended {n} sales trainings",
    ],
    "IT": [
        "Fixed {n} critical bugs",
        "Optimized database queries",
        "Deployed version {v}.{n}",
    ],
    "default": [
        "Team collaboration meeting",
        "Project planning session",
        "Cross-department alignment",
    ],
}

try:
    # 建立连接
    with pymysql.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            # 清空现有数据（TRUNCATE更快但会重置自增ID）
            cursor.execute("TRUNCATE TABLE activities")

            # 生成10名员工10周的数据
            for emp_id in range(1, 11):
                # 生成员工基本信息
                name = fake.name()
                email = (
                    f"{name.split()[0][0].lower()}{name.split()[1].lower()}@company.com"
                )
                dept = random.choice(departments)
                job = random.choice(job_titles[dept])
                hire_date = fake.date_between(start_date="-2y", end_date="-3mo")

                # 生成10周数据
                for week in range(1, 11):
                    # 生成数值数据
                    num_meetings = random.randint(2, 10)
                    hours_worked = round(random.uniform(30, 50), 1)
                    total_sales = (
                        round(random.uniform(5000, 50000), 2)
                        if dept == "Sales"
                        else 0.0
                    )

                    # 生成活动描述
                    if dept in activity_templates:
                        activities = [
                            t.format(
                                n=random.randint(1, 5),
                                quarter=random.randint(1, 4),
                                v=random.randint(1, 3),
                            )
                            for t in random.sample(activity_templates[dept], 2)
                        ]
                    else:
                        activities = random.sample(activity_templates["default"], 2)
                    activities_str = "; ".join(activities)

                    # 插入数据（注意参数占位符为%s）
                    cursor.execute(
                        """INSERT INTO activities 
                        (employee_id, week_number, num_meetings, total_sales_rmb, 
                         hours_worked, activities, department, hire_date, email, job_title)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            f"EMP{emp_id:03d}",
                            week,
                            num_meetings,
                            total_sales,
                            hours_worked,
                            activities_str,
                            dept,
                            hire_date,
                            email,
                            job,
                        ),
                    )

            # 提交事务
            conn.commit()
            print(f"成功生成10名员工×10周=100条数据！")

except pymysql.MySQLError as e:
    print(f"数据库错误: {e}")
    if "conn" in locals():
        conn.rollback()
except Exception as e:
    print(f"其他错误: {e}")
finally:
    if "conn" in locals() and conn.open:
        conn.close()
