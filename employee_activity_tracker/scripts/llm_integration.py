# # scripts/llm_integration.py
# import os
# from openai import OpenAI
# from pathlib import Path
# from typing import Optional

# # 环境变量配置
# env_path = Path(__file__).parent.parent / ".env"
# if env_path.exists():
#     from dotenv import load_dotenv

#     load_dotenv(env_path)

# # 初始化客户端
# client = OpenAI(
#     api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量获取密钥
#     base_url="https://api.deepseek.com",  # 官方指定端点
# )


# def query_to_sql(natural_language_query: str, table_schema: str) -> Optional[str]:
#     """
#     使用DeepSeek官方API将自然语言转换为SQL
#     """
#     prompt = f"""
#     你是一个专业的SQL工程师，根据以下表结构将自然语言查询转换为MySQL语法：
#     【表结构】
#     {table_schema}

#     【规则】
#     1. 只返回纯SQL语句，不要任何解释或标记
#     2. 使用WHERE而非HAVING
#     3. 日期比较用DATE()函数
#     4. 确保字段名和表名完全匹配

#     【用户查询】
#     {natural_language_query}
#     """

#     try:
#         response = client.chat.completions.create(
#             model="deepseek-chat",  # 或使用 "deepseek-reasoner"
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.1,
#             max_tokens=200,
#             stream=False,
#         )
#         sql = response.choices[0].message.content.strip()

#         # 安全校验
#         if not sql.startswith(("SELECT", "INSERT", "UPDATE", "DELETE")):
#             raise ValueError("非法的SQL语句类型")
#         return sql
#     except Exception as e:
#         print(f"⚠️ DeepSeek API错误: {e}")
#         return None


# def test():
#     schema = "activities(id, employee_id, department, hours_worked, hire_date)"
#     queries = [
#         "销售部工时最高的员工",
#         "2023年入职的IT部门员工",
#         "会议数超过5次且工时低于40小时的员工",
#     ]
#     for q in queries:
#         print(f"\n输入: {q}")
#         sql = query_to_sql(q, schema)
#         print(f"输出: {sql}")


# if __name__ == "__main__":
#     test()


# # scripts/llm_integration.py
# import os
# from openai import OpenAI
# from pathlib import Path
# from typing import Optional

# # 环境变量配置
# env_path = Path(__file__).parent.parent / ".env"
# if env_path.exists():
#     from dotenv import load_dotenv

#     load_dotenv(env_path)

# # 初始化客户端
# client = OpenAI(
#     api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
# )


# def query_to_sql(natural_language_query: str, table_schema: str) -> Optional[str]:
#     """
#     优化后的DeepSeek SQL生成函数
#     """
#     prompt = f"""
#     # 角色
#     你是一个专业的MySQL数据库工程师，专注于将自然语言查询转换为精确的SQL语句。

#     # 数据库表结构
#     {table_schema}

#     # 任务
#     将以下查询转换为MySQL语法，严格遵守规则：

#     # 规则
#     1. **只输出SQL语句**，不要包含任何解释、标记或注释
#     2. 必须使用以下语法结构之一开头：
#        - SELECT
#        - WITH (CTE查询)
#     3. 禁止使用这些操作：
#        - DROP, DELETE, UPDATE, INSERT, ALTER
#     4. 字段引用格式：
#        - 直接使用字段名（如 `department`）
#        - 不要使用反引号或引号包裹
#     5. 日期处理：
#        - 使用 `DATE(hire_date)` 处理日期
#        - 年份比较用 `YEAR(hire_date) = 2023`

#     # 用户查询
#     {natural_language_query}

#     # 输出要求
#     只需输出符合上述规则的SQL语句，不要包含其他任何内容！
#     """

#     try:
#         response = client.chat.completions.create(
#             model="deepseek-chat",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.1,
#             max_tokens=200,
#         )
#         sql = response.choices[0].message.content.strip()

#         # 严格验证SQL格式
#         if not _validate_sql(sql):
#             raise ValueError("SQL语法验证失败")
#         return sql

#     except Exception as e:
#         print(f"⚠️ DeepSeek API错误: {e}")
#         return None


# def _validate_sql(sql: str) -> bool:
#     """验证SQL是否符合安全规则"""
#     allowed_prefixes = ("SELECT", "WITH")
#     forbidden_commands = ("DROP", "DELETE", "UPDATE", "INSERT", "ALTER")

#     return sql.upper().startswith(allowed_prefixes) and not any(
#         cmd in sql.upper() for cmd in forbidden_commands
#     )


# # 测试函数
# def test():
#     schema = """
#     activities(
#         id INT,
#         employee_id VARCHAR(20),
#         department VARCHAR(50),
#         hours_worked DECIMAL(5,1),
#         hire_date DATE,
#         num_meetings INT
#     )
#     """
#     test_cases = [
#         "销售部工时最高的员工",
#         "2023年入职的IT部门员工",
#         "会议数超过5次且工时低于40小时的员工",
#     ]

#     for query in test_cases:
#         print(f"\n输入: {query}")
#         sql = query_to_sql(query, schema)
#         print(f"输出: {sql}")


# if __name__ == "__main__":
#     test()


# scripts/llm_integration.py
import os
from openai import OpenAI
from pathlib import Path
from typing import Optional, Any, List, Dict, Union
import mysql.connector  # 新增：数据库连接

# 环境变量配置
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv

    load_dotenv(env_path)

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
)

# 新增：数据库连接配置（示例，实际应从环境变量获取）
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "analytics"),
}


def get_db_connection():
    """新增：获取数据库连接"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"⚠️ 数据库连接失败: {e}")
        return None


def query_to_sql(natural_language_query: str, table_schema: str) -> Optional[str]:
    """
    优化后的DeepSeek SQL生成函数
    （保持不变）
    """
    prompt = f"""
    # 角色
    你是一个专业的MySQL数据库工程师，专注于将自然语言查询转换为精确的SQL语句。

    # 数据库表结构
    {table_schema}

    # 任务
    将以下查询转换为MySQL语法，严格遵守规则：

    # 规则
    1. **只输出SQL语句**，不要包含任何解释、标记或注释
    2. 必须使用以下语法结构之一开头：
       - SELECT
       - WITH (CTE查询)
    3. 禁止使用这些操作：
       - DROP, DELETE, UPDATE, INSERT, ALTER
    4. 字段引用格式：
       - 直接使用字段名（如 `department`）
       - 不要使用反引号或引号包裹
    5. 日期处理：
       - 使用 `DATE(hire_date)` 处理日期
       - 年份比较用 `YEAR(hire_date) = 2023`

    # 用户查询
    {natural_language_query}

    # 输出要求
    只需输出符合上述规则的SQL语句，不要包含其他任何内容！
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200,
        )
        sql = response.choices[0].message.content.strip()

        if not _validate_sql(sql):
            raise ValueError("SQL语法验证失败")
        return sql
    except Exception as e:
        print(f"⚠️ DeepSeek API错误: {e}")
        return None


def _validate_sql(sql: str) -> bool:
    """验证SQL是否符合安全规则（保持不变）"""
    allowed_prefixes = ("SELECT", "WITH")
    forbidden_commands = ("DROP", "DELETE", "UPDATE", "INSERT", "ALTER")
    return sql.upper().startswith(allowed_prefixes) and not any(
        cmd in sql.upper() for cmd in forbidden_commands
    )


# 新增核心功能 ==============================================
def query_to_natural_language(
    query: str,
    table_schema: str,
    analysis_type: str = "auto",  # 'auto'|'numerical'|'qualitative'
) -> str:
    """
    端到端自然语言查询处理
    输入: 自然语言问题 + 表结构
    输出: 自然语言回答
    """
    # 1. 生成SQL
    sql = query_to_sql(query, table_schema)
    if not sql:
        return "❌ 无法生成有效的数据库查询。"

    # 2. 执行查询
    db_conn = get_db_connection()
    if not db_conn:
        return "❌ 数据库连接失败"

    try:
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchall()
    except Exception as e:
        return f"❌ 查询执行失败: {str(e)}"
    finally:
        db_conn.close()

    # 3. 转换为自然语言
    return _results_to_natural_language(
        query=query, results=results, analysis_type=analysis_type
    )


def _results_to_natural_language(
    query: str, results: List[Dict[str, Any]], analysis_type: str
) -> str:
    """将查询结果转换为自然语言"""
    prompt = f"""
    # 任务
    根据数据库查询结果，用自然语言回答用户问题。
    
    # 用户问题
    {query}

    # 查询结果 (JSON格式)
    {results}

    # 回答要求
    1. 根据分析类型重点处理：
       - "numerical": 突出数字和统计信息
       - "qualitative": 分析模式和趋势
       - "auto": 自动判断最佳方式
    2. 如果结果为空，说明"未找到相关数据"
    3. 使用英文回答，保持专业但易懂
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 回答生成失败: {str(e)}"


def benchmark_test():
    """运行所有20个示例查询的基准测试"""
    schema = """
    activities(
        id INT, 
        employee_id VARCHAR(20), 
        week_number INT,
        num_meetings INT,
        total_sales_rmb DECIMAL(10, 2),
        hours_worked DECIMAL(5, 1),
        activities TEXT,
        department VARCHAR(50),
        hire_date DATE,
        email VARCHAR(100),
        job_title VARCHAR(100)
    )
    """

    # 20个示例查询
    queries = [
        "What is the email address of the employee who is the Sales Manager?",
        "Which employee in the company works in the Product Development department?",
        "What was the sales revenue of 'Wei Zhang' for the week starting on '2024-08-28'?",
        "Who are the employees working in the 'Finance' department?",
        "Retrieve the total number of meetings attended by 'Na Li' in her weekly updates.",
        "Which employees worked more than 40 hours during week 1?",
        "How many employees does the company have in total?",
        "What is the average hours worked by all employees during week 2?",
        "How much total sales revenue has the Sales department generated to date?",
        "What is the total sales revenue generated by the company during week 1?",
        "Who worked the most hours during the first week of September 2024?",
        "Which employee attended the most meetings during week 2?",
        "Which employees in the company were hired during a time of industry recession?",
        "Who are the employees that faced challenges with customer retention, and what solutions did they propose?",
        "Which employees work in roles that likely require data analysis or reporting skills?",
        "List all employees who work in the IT department within the company.",
        "Compare the hours worked by 'Wei Zhang' and 'Tao Huang' during week 1.",
        "Who are the top 3 employees by total hours worked during the last 4 weeks?",
        "Who achieved the highest sales revenue in a single week, and when?",
        "What is the total number of hours worked and average sales revenue for employees in the Business Development department?",
    ]

    print("\n=== 基准测试 ===\n")
    results = []

    for i, query in enumerate(queries, 1):
        print(f"查询 {i}/20: {query}")

        # 生成SQL
        sql = query_to_sql(query, schema)
        print(f"SQL: {sql}")

        # 执行查询并生成回答
        answer = query_to_natural_language(query, schema, "auto")
        print(f"回答:\n{answer}\n")
        print("-" * 80)

        # 保存结果
        results.append({"query_id": i, "query": query, "sql": sql, "answer": answer})

    # 可选：将结果保存到文件
    import json

    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n基准测试完成，结果已保存到 benchmark_results.json")


# 测试函数 ==============================================
def test():
    schema = """
    activities(
        id INT, 
        employee_id VARCHAR(20), 
        department VARCHAR(50),
        hours_worked DECIMAL(5,1),
        hire_date DATE,
        num_meetings INT
    )
    """

    # 原SQL生成测试（保留）
    print("\n=== SQL生成测试 ===")
    sql_test_cases = [
        "销售部工时最高的员工",
        "2023年入职的IT部门员工",
    ]
    for query in sql_test_cases:
        print(f"\n输入: {query}")
        sql = query_to_sql(query, schema)
        print(f"SQL: {sql}")

    # 新增：自然语言回答测试
    print("\n=== 自然语言回答测试 ===")
    nl_test_cases = [
        ("销售部上周平均工时是多少？", "numerical"),
        ("描述各部门的会议分布情况", "qualitative"),
        ("工时超过40小时的员工有哪些？", "auto"),
    ]

    for query, analysis_type in nl_test_cases:
        print(f"\n问题: {query}")
        answer = query_to_natural_language(query, schema, analysis_type)
        print(f"回答:\n{answer}")


if __name__ == "__main__":
    test()
    benchmark_test()  # 运行基准测试
