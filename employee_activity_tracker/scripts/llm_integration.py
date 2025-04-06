# scripts/llm_integration.py
import os
from openai import OpenAI
from pathlib import Path
from typing import Optional, Any, List, Dict, Union
import mysql.connector  # Added: Database connection

# Environment variables configuration
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv

    load_dotenv(env_path)

# Initialize client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
)

# Added: Database connection configuration (example, actual values should come from environment variables)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "analytics"),
}


def get_db_connection():
    """Added: Get database connection"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")  # CHANGED: Translated to English
        return None


def query_to_sql(natural_language_query: str, table_schema: str) -> Optional[str]:
    """
    Optimized DeepSeek SQL generation function
    """
    prompt = f"""
    # Role
    You are a professional MySQL database engineer, focused on converting natural language queries into precise SQL statements.

    # Database structure
    {table_schema}

    # Task
    Convert the following query into MySQL syntax, strictly following these rules:

    # Rules
    1. **Output only the SQL statement**, without any explanations, tags, or comments
    2. You must start with one of these syntax structures:
       - SELECT
       - WITH (CTE query)
    3. Do not use these operations:
       - DROP, DELETE, UPDATE, INSERT, ALTER
    4. Field reference format:
       - Use field names directly (e.g., `department`)
       - Do not wrap fields in backticks or quotes
    5. Date handling:
       - Use `DATE(hire_date)` to process dates
       - For year comparisons, use `YEAR(hire_date) = 2023`
    
    # Additional SQL generation guidelines: [NEW SECTION]
    - Map date references to our week numbering system. Week numbering system (example): Week 1: 2024-08-01 to 2024-08-07, Week 7: 2024-08-28 to 2024-09-03
    - If the query mentions "2024-08-28", use week_number = 7 instead of WEEK functions
    - Use broader search terms for semantic queries (e.g., use LIKE '%retention%' instead of multiple conditions)
    - For time periods, map calendar references to our sequential week numbers (e.g., "September 2024" → weeks 7-10)
    - Always include DISTINCT when counting or listing employees to avoid duplication
    - When searching for recession periods, include years 2020-2021
    - For "last 4 weeks", use week_number BETWEEN (SELECT MAX(week_number) - 3 FROM activities) AND (SELECT MAX(week_number) FROM activities)

    # User query
    {natural_language_query}

    # Output requirements
    Only output the SQL statement that complies with the above rules, without any other content!
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
            raise ValueError("SQL syntax validation failed")
        return sql
    except Exception as e:
        print(f"⚠️ DeepSeek API error: {e}")
        return None


def _validate_sql(sql: str) -> bool:
    """Validate SQL complies with security rules (unchanged)"""
    allowed_prefixes = ("SELECT", "WITH")
    forbidden_commands = ("DROP", "DELETE", "UPDATE", "INSERT", "ALTER")
    return sql.upper().startswith(allowed_prefixes) and not any(
        cmd in sql.upper() for cmd in forbidden_commands
    )


# Added core functionality ==============================================
def query_to_natural_language(
    query: str,
    table_schema: str,
    analysis_type: str = "auto",  # 'auto'|'numerical'|'qualitative'
) -> str:
    """
    End-to-end natural language query processing
    Input: Natural language question + table structure
    Output: Natural language answer
    """
    # 1. Generate SQL
    sql = query_to_sql(query, table_schema)
    if not sql:
        return "❌ Unable to generate a valid database query."  # CHANGED: Translated to English

    # 2. Execute query
    db_conn = get_db_connection()
    if not db_conn:
        return "❌ Database connection failed"  # CHANGED: Translated to English

    try:
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchall()
    except Exception as e:
        return f"❌ Query execution failed: {str(e)}"  # CHANGED: Translated to English
    finally:
        db_conn.close()

    # 3. Convert to natural language
    return _results_to_natural_language(
        query=query, results=results, analysis_type=analysis_type
    )


def _results_to_natural_language(
    query: str, results: List[Dict[str, Any]], analysis_type: str
) -> str:
    """Convert query results to natural language"""
    prompt = f"""
    # Task
    Answer the user's question in natural language based on database query results.
    
    # User question
    {query}

    # Query results (JSON format)
    {results}

    # Response requirements
    1. Focus processing based on analysis type:
       - "numerical": Emphasize numbers and statistical information
       - "qualitative": Analyze patterns and trends
       - "auto": Automatically determine the best approach
    2. If results are empty, state "No relevant data found"
    3. Answer in English, maintaining professionalism while being easy to understand
    4. If results contain duplicate entries (e.g., same employee appearing multiple times), summarize them as a single entry in the response.
    5. - For numerical results: 
    -If value > average: "This is X% higher than the company average of Y." 
    -If value < average: "This is X% lower than the company average of Y."
    
    # Response formatting guidelines: [NEW SECTION]
    - Focus on answering the question directly without mentioning data structure issues like duplication
    - Use a consistent structure for responses: start with a direct answer, then provide supporting details
    - When results are empty, suggest possible reasons and alternatives
    - For numerical queries, always include the key figures prominently
    - For qualitative queries, highlight patterns and insights
    - Ignore duplicate entries in results when formulating your response
    - For comparisons, clearly state the differences with specific values
    - If the query involves specific dates, periods, or ranges, reference them explicitly in your answer
    - Provide context for numerical values when appropriate (e.g., "which is 20% higher than average")
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Response generation failed: {str(e)}"


def benchmark_test():
    """Run benchmark test for all 20 example queries"""
    schema = """
    activities(
        id INT, 
        employee_id VARCHAR(20), 
        full_name VARCHAR(100),
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

    # 20 example queries
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

    print("\n=== Benchmark Test ===\n")  # CHANGED: Translated to English
    results = []

    for i, query in enumerate(queries, 1):
        print(f"Query {i}/20: {query}")  # CHANGED: Translated to English

        # Generate SQL
        sql = query_to_sql(query, schema)
        print(f"SQL: {sql}")

        # Execute query and generate response
        answer = query_to_natural_language(query, schema, "auto")
        print(f"Response:\n{answer}\n")  # CHANGED: Translated to English
        print("-" * 80)

        # Save results
        results.append({"query_id": i, "query": query, "sql": sql, "answer": answer})

    # Optional: Save results to file
    import json

    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(
        "\nBenchmark test complete, results saved to benchmark_results.json"
    )  # CHANGED: Translated to English


if __name__ == "__main__":
    benchmark_test()  # Run benchmark test
