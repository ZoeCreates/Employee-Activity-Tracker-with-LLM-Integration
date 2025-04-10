
# 📊 How to Use the System

This guide walks you through how to run the project **from scratch**, including container setup, database initialization, and LLM-powered querying.

## ✅ Step 1: Create the `.env` file

In the project root directory (same level as `docker-compose.yml`), create a `.env` file:

```bash
nano .env
```

Paste the following content (replace the API key with your actual one):

```
# 数据库配置
DB_HOST=mysql
DB_USER=root
DB_PASSWORD=123456
DB_NAME=employee_tracking
MYSQL_PASSWORD=123456
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

## ✅ Step 2: Start services with Docker

```bash
docker-compose up -d
```

This will start:
* 🗄️ MySQL container (`mysql_dev`)
* 🐍 Python app container (`employee_activity_tracker-app-1`)

✅ Check everything is running with:

```bash
docker-compose ps
```

You should see `mysql_dev` as `healthy`.

## ✅ Step 3: Initialize the database (run once)

This creates the `activities` table.

```bash
docker-compose exec app python init_db_runner.py
```

Expected output:

```
✅ Database initialized successfully.
```

## ✅ Step 4: Populate with sample employee data

```bash
docker-compose exec app python populate_data.py
```

Expected output:

```
Successfully generated data for 10 employees × 10 weeks = 100 records
```

## ✅ Step 5: Generate visual reports (charts)

```bash
docker-compose exec app python visualize_db.py
```

You'll find charts in:

```bash
scripts/visualizations/
```

## ✅ Step 6: Run the LLM benchmark test

This will convert 20 natural language questions into SQL, run them, and produce readable answers.

```bash
docker-compose exec app python llm_integration.py
```

Output is saved to:

```bash
scripts/benchmark_results.json
```

## 🧪 Cold Start Verification

✅ This project has been fully tested on a clean GitHub clone as of **2025-04-06**.
You can clone it, run the above steps, and everything should work from scratch.

## ⚠️ Common Mistakes & Fixes

### 1. `init_db.sql` is a **folder**, not a file:

**Symptom:**
```
IsADirectoryError: [Errno 21] Is a directory: 'init_db.sql'
```

**Fix:**
```bash
rm -r scripts/init_db.sql
nano scripts/init_db.sql # Then paste the CREATE TABLE SQL content
```

```sql
-- 创建数据库（如果不存在）Create the database if not existed 
CREATE DATABASE IF NOT EXISTS employee_tracking;
USE employee_tracking;

-- 创建员工活动表 Create the employee table
CREATE TABLE IF NOT EXISTS activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL,
    full_name VARCHAR(100) NOT NULL, -- <<< newly added 
    week_number INT,
    num_meetings INT,
    total_sales_rmb DECIMAL(10, 2),
    hours_worked DECIMAL(5, 1),
    activities TEXT,
    department VARCHAR(50),
    hire_date DATE,
    email VARCHAR(100),
    job_title VARCHAR(100),
    INDEX (employee_id),
    INDEX (department),
    INDEX (full_name) 
);
```

### 2. MySQL container failed to start

**Symptom:**
```
Container mysql_dev exited (1)
```

**Likely Cause:**
You forgot to add this line in `.env`:

```
MYSQL_ROOT_PASSWORD=123456
```

**Fix:**
* Add that line to `.env`
* Then restart containers:

```bash
docker-compose down
docker-compose up -d
```

### 3. LLM query fails due to missing API key

**Symptom:**
```
OpenAIError: The api_key client option must be set...
```

**Fix:**
Ensure this line exists in your `.env`:

```
DEEPSEEK_API_KEY=your-deepseek-api-key
```

Then restart:

```bash
docker-compose down
docker-compose up -d
```

## 🏁 Done!

If you've completed all steps, you now have:
* ✅ A running MySQL + Python containerized system
* ✅ Visual analytics of employee behavior
* ✅ Natural language to SQL conversion powered by DeepSeek LLM

## System Visualization

![image](https://github.com/user-attachments/assets/0505411a-07df-4ad4-8f72-03287b3679ed)


## Json File for the Example llm Q#A 


[
  {
    "query_id": 1,
    "query": "What is the email address of the employee who is the Sales Manager?",
    "sql": "SELECT email\nFROM activities\nWHERE job_title = 'Sales Manager'\nLIMIT 1;",
    "answer": "The email address of the Sales Manager is **w.zhang@company.com**.  \n\n*Supporting detail*: This information is based on the query results provided. No further context or comparison is required for this qualitative response.  \n\n(Note: Since this is a straightforward lookup query without numerical values or duplicates, the response adheres to the \"auto\" analysis type by providing a direct answer.)"
  },
  {
    "query_id": 2,
    "query": "Which employee in the company works in the Product Development department?",
    "sql": "SELECT DISTINCT employee_id, full_name\nFROM activities\nWHERE department = 'Product Development';",
    "answer": "# Response  \n\nThe employee who works in the Product Development department is **Tao Huang** (Employee ID: EMP003).  \n\nThis is a qualitative response based on the provided data. No further statistical comparisons or trends are applicable in this case.  \n\nLet me know if you'd like additional details about this employee or the department."
  },
  {
    "query_id": 3,
    "query": "What was the sales revenue of 'Wei Zhang' for the week starting on '2024-08-28'?",
    "sql": "SELECT total_sales_rmb\nFROM activities\nWHERE full_name = 'Wei Zhang' AND week_number = 7;",
    "answer": "**Response:**  \n\nWei Zhang's sales revenue for the week starting on **2024-08-28** was **28,000 RMB**.  \n\n*(Note: No company average data was provided for comparison. If additional context is needed, please specify the benchmark or historical data for further analysis.)*  \n\n---  \n**Structure adherence:**  \n- Direct answer first, followed by contextual details.  \n- Key numerical value (**28,000 RMB**) emphasized.  \n- Explicit reference to the date range (week starting 2024-08-28).  \n- Professional tone with clarity.  \n- No duplication handling required (single entry in results).  \n- Missing comparison metrics acknowledged transparently."
  },
  {
    "query_id": 4,
    "query": "Who are the employees working in the 'Finance' department?",
    "sql": "SELECT DISTINCT employee_id, full_name\nFROM activities\nWHERE department = 'Finance';",
    "answer": "The employees working in the 'Finance' department are:  \n- Min Chen (Employee ID: EMP004)  \n- Xue Wu (Employee ID: EMP008)  \n\nThis is a qualitative response based on the provided data. No duplicates or numerical comparisons were required for this query.  \n\n(Note: Since the analysis type was set to \"auto,\" the response prioritizes clear listing of qualitative results without statistical emphasis.)"
  },
  {
    "query_id": 5,
    "query": "Retrieve the total number of meetings attended by 'Na Li' in her weekly updates.",
    "sql": "SELECT SUM(num_meetings) \nFROM activities \nWHERE full_name = 'Na Li';",
    "answer": "# Response  \n\n**Na Li attended a total of 38 meetings in her weekly updates.**  \n\n*(Note: Since no company average data was provided for comparison, a relative performance assessment cannot be made.)*  \n\nThis numerical result reflects her meeting participation over the observed period. If further context—such as time frame or team averages—is available, a more detailed analysis could be provided.  \n\n---  \n*Response type: Numerical (auto-detected). Key figure emphasized directly. No duplicates detected in results.*"
  },
  {
    "query_id": 6,
    "query": "Which employees worked more than 40 hours during week 1?",
    "sql": "SELECT DISTINCT employee_id, full_name\nFROM activities\nWHERE week_number = 1 AND hours_worked > 40;",
    "answer": "**Response:**  \n\nThe following employees worked more than 40 hours during week 1:  \n- Wei Zhang (EMP001)  \n- Tao Huang (EMP003)  \n- Min Chen (EMP004)  \n- Qiang Wang (EMP005)  \n- Xue Wu (EMP008)  \n- Fang Xu (EMP010)  \n\nA total of **6 employees** exceeded the 40-hour threshold in the given week.  \n\n*(Note: Since no average data was provided in the query results, a comparative analysis against company averages cannot be included.)*"
  },
  {
    "query_id": 7,
    "query": "How many employees does the company have in total?",
    "sql": "SELECT COUNT(DISTINCT employee_id) FROM activities;",
    "answer": "# Response  \n\n**The company has a total of 10 employees.**  \n\n*(Analysis type: Numerical - The response focuses on the exact count of distinct employees without additional comparative data since no average is provided.)*  \n\n---  \n**Key Notes:**  \n- The count reflects unique employees (duplicates removed).  \n- No comparative benchmark is available to assess whether this number is above or below average.  \n- For further insights, additional context (e.g., department-wise breakdown or historical trends) would be helpful."
  },
  {
    "query_id": 8,
    "query": "What is the average hours worked by all employees during week 2?",
    "sql": "SELECT AVG(hours_worked) FROM activities WHERE week_number = 2;",
    "answer": "# Response  \n\nThe average hours worked by all employees during week 2 was **41.3 hours**.  \n\n*(Analysis type: Numerical)*  \n\nSince no company-wide average was provided in the query results, a direct comparison cannot be made. If additional context is needed, further data on overall averages would be required.  \n\nWould you like a breakdown by department or a comparison to other weeks?"
  },
  {
    "query_id": 9,
    "query": "How much total sales revenue has the Sales department generated to date?",
    "sql": "SELECT SUM(total_sales_rmb) \nFROM activities \nWHERE department = 'Sales';",
    "answer": "The Sales department has generated a total sales revenue of **RMB 881,945.36** to date.  \n\n*(Note: Since no company average was provided in the query results, a comparative analysis cannot be performed.)*"
  },
  {
    "query_id": 10,
    "query": "What is the total sales revenue generated by the company during week 1?",
    "sql": "SELECT SUM(total_sales_rmb) \nFROM activities \nWHERE week_number = 1;",
    "answer": "The total sales revenue generated by the company during week 1 was **93,000 RMB**.  \n\n*(Note: Since no company average was provided in the query results, a comparative statement cannot be included. If additional context is needed, please provide the average sales revenue for reference.)*"
  },
  {
    "query_id": 11,
    "query": "Who worked the most hours during the first week of September 2024?",
    "sql": "SELECT full_name, hours_worked \nFROM activities \nWHERE week_number BETWEEN 7 AND 10 \nORDER BY hours_worked DESC \nLIMIT 1;",
    "answer": "**Response:**  \n\nQiang Wang worked the most hours during the first week of September 2024, with a total of **49.0 hours**.  \n\n*(Note: Since no company average was provided in the query results, a comparative percentage analysis could not be included.)*  \n\n---  \n**Structure adherence:**  \n- Direct answer first, followed by supporting details.  \n- Key numerical value (**49.0 hours**) emphasized.  \n- Explicit reference to the time period (first week of September 2024).  \n- Professional tone with clarity.  \n- No duplication issues detected in results."
  },
  {
    "query_id": 12,
    "query": "Which employee attended the most meetings during week 2?",
    "sql": "SELECT employee_id, full_name, num_meetings\nFROM activities\nWHERE week_number = 2\nORDER BY num_meetings DESC\nLIMIT 1;",
    "answer": "# Response  \n\n**Direct Answer:**  \nNa Li (EMP002) attended the most meetings during week 2, with a total of 8 meetings.  \n\n**Supporting Details:**  \nThis is a numerical result, and no comparison data (e.g., company average) is provided for further context. If additional statistical benchmarks were available, we could assess whether this figure is above or below the typical participation rate.  \n\n*(Note: Since the query results contain only one entry, no deduplication was needed. The response adheres to a clear, structured format with emphasis on the key numerical value.)*"
  },
  {
    "query_id": 13,
    "query": "Which employees in the company were hired during a time of industry recession?",
    "sql": "SELECT DISTINCT employee_id, full_name\nFROM activities\nWHERE YEAR(hire_date) BETWEEN 2020 AND 2021;",
    "answer": "**Response:**  \n\nThe following employees were hired during a time of industry recession:  \n- Min Chen (EMP004)  \n- Qiang Wang (EMP005)  \n- Xue Wu (EMP008)  \n- Jie Zhou (EMP009)  \n\nThis suggests that the company continued hiring during economically challenging periods, potentially indicating strategic workforce planning or resilience in recruitment. If further analysis is needed—such as comparing hiring trends during recessions versus growth periods—additional data could provide deeper insights.  \n\n*(Analysis type: Qualitative - Focused on identifying patterns in hiring during recessions.)*"
  },
  {
    "query_id": 14,
    "query": "Who are the employees that faced challenges with customer retention, and what solutions did they propose?",
    "sql": "SELECT DISTINCT employee_id, full_name, activities\nFROM activities\nWHERE activities LIKE '%customer retention%'\n OR activities LIKE '%retention%'\n OR activities LIKE '%engagement%'\n OR activities LIKE '%feedback%'\n OR activities LIKE '%challenge%'\n OR activities LIKE '%solution%'",
    "answer": "**Response:**  \n\nThe employees who faced challenges with customer retention and their proposed solutions are:  \n\n1. **Wei Zhang (EMP001)** – Focused on customer retention strategy planning as part of their activities.  \n2. **Yue Lin (EMP006)** – Identified customer retention issues and implemented a discount strategy for at-risk accounts.  \n3. **Jie Zhou (EMP009)** – Analyzed customer retention issues and launched a targeted email campaign to re-engage dormant customers.  \n\n**Supporting Details:**  \n- **Yue Lin** and **Jie Zhou** took direct action by introducing a discount strategy and an email campaign, respectively, to address retention challenges.  \n- **Wei Zhang** contributed to strategic planning, indicating a proactive approach to improving retention.  \n\nThis analysis highlights both problem identification and solution implementation by the team. Let me know if you'd like further details on any specific initiative."
  },
  {
    "query_id": 15,
    "query": "Which employees work in roles that likely require data analysis or reporting skills?",
    "sql": "SELECT DISTINCT employee_id, full_name, job_title\nFROM activities\nWHERE job_title LIKE '%data%' \n   OR job_title LIKE '%analyst%' \n   OR job_title LIKE '%reporting%' \n   OR job_title LIKE '%BI%' \n   OR job_title LIKE '%business intelligence%' \n   OR job_title LIKE '%analytics%';",
    "answer": "Here’s the response following the provided guidelines:\n\n---\n\n**Direct Answer:**  \nThree employees work in roles that likely require data analysis or reporting skills:  \n1. Min Chen (Financial Analyst)  \n2. Qiang Wang (Data Engineer)  \n3. Jie Zhou (SEO Analyst)  \n\n**Supporting Details:**  \n- **Financial Analysts** typically handle numerical data, financial reporting, and statistical modeling.  \n- **Data Engineers** focus on building systems for data processing and analysis.  \n- **SEO Analysts** often analyze qualitative and quantitative web data to optimize performance.  \n\nNo duplicates were found in the results.  \n\n*(Analysis type: \"auto\" — response combines qualitative role descriptions with clear enumeration of results.)*  \n\n--- \n\nLet me know if you'd like further details about specific roles or skills!"
  },
  {
    "query_id": 16,
    "query": "List all employees who work in the IT department within the company.",
    "sql": "SELECT DISTINCT employee_id, full_name\nFROM activities\nWHERE department = 'IT';",
    "answer": "Here is the response to the user's question following all specified requirements and formatting guidelines:\n\n**Direct Answer:**  \nThe employees working in the IT department are:  \n- Qiang Wang (Employee ID: EMP005)  \n- Yang Zhao (Employee ID: EMP007)  \n\n**Supporting Details:**  \n- Total IT employees listed: **2**.  \n- No duplicates were detected in the results.  \n\nThis is a qualitative response, as the task involves listing specific individuals rather than numerical analysis. The results are presented clearly without referencing data structure issues.  \n\n*(Note: Since no averages or numerical comparisons were requested, those formatting rules were not applied.)*"
  },
  {
    "query_id": 17,
    "query": "Compare the hours worked by 'Wei Zhang' and 'Tao Huang' during week 1.",
    "sql": "SELECT full_name, hours_worked\nFROM activities\nWHERE full_name IN ('Wei Zhang', 'Tao Huang') AND week_number = 1\nORDER BY full_name;",
    "answer": "**Response:**  \n\nDuring week 1, Wei Zhang worked **42.5 hours**, while Tao Huang worked **41 hours**. This means Wei Zhang worked **1.5 hours more** than Tao Huang that week.  \n\n*(Note: No company average data was provided for additional context.)*  \n\n---  \n**Structure adherence:**  \n- Direct numerical comparison upfront  \n- Specific values highlighted  \n- Clear difference quantified  \n- Professional yet concise tone  \n- No duplication issues to address  \n- Follows \"numerical\" emphasis per auto-detected analysis type"
  },
  {
    "query_id": 18,
    "query": "Who are the top 3 employees by total hours worked during the last 4 weeks?",
    "sql": "SELECT DISTINCT employee_id, full_name, SUM(hours_worked) AS total_hours\nFROM activities\nWHERE week_number BETWEEN (SELECT MAX(week_number) - 3 FROM activities) AND (SELECT MAX(week_number) FROM activities)\nGROUP BY employee_id, full_name\nORDER BY total_hours DESC\nLIMIT 3;",
    "answer": "**Top 3 Employees by Total Hours Worked (Last 4 Weeks):**  \n\n1. **Xue Wu (EMP008)** and **Qiang Wang (EMP005)** tied for the highest at **196 hours** each.  \n2. **Fang Xu (EMP010)** followed closely with **192 hours**.  \n\n*(Note: No company average was provided for comparison.)*  \n\nThis response focuses on the numerical results, presenting the key figures prominently while maintaining clarity. The tie between the top two employees is explicitly noted, and the absence of comparative data is acknowledged transparently."
  },
  {
    "query_id": 19,
    "query": "Who achieved the highest sales revenue in a single week, and when?",
    "sql": "SELECT full_name, week_number, MAX(total_sales_rmb) AS max_sales\nFROM activities\nGROUP BY full_name, week_number\nORDER BY max_sales DESC\nLIMIT 1;",
    "answer": "**Response:**  \n\nFang Xu achieved the highest sales revenue in a single week, with **52,000 RMB** during **week 7**.  \n\n*(Note: Since no company average was provided in the query results, a comparative percentage analysis could not be included. If additional context is needed, please provide the average sales revenue for such comparisons.)*  \n\n---  \n**Structure adherence:**  \n1. **Direct answer** first, followed by supporting details.  \n2. **Key numerical values** (52,000 RMB, week 7) are highlighted.  \n3. **Professional yet clear** language.  \n4. **Contextual note** added for missing comparative data.  \n\nLet me know if you'd like further analysis (e.g., trends, historical comparisons)."
  },
  {
    "query_id": 20,
    "query": "What is the total number of hours worked and average sales revenue for employees in the Business Development department?",
    "sql": "SELECT \n    SUM(hours_worked) AS total_hours_worked,\n    AVG(total_sales_rmb) AS average_sales_revenue\nFROM \n    activities\nWHERE \n    department = 'Business Development';",
    "answer": "No relevant data found for the total number of hours worked and average sales revenue in the Business Development department.  \n\nThis could be due to:  \n- No employees currently assigned to this department  \n- Missing or incomplete records for the specified metrics  \n- The department may not have any recorded work hours or sales revenue data  \n\nIf you need this information, you may want to verify the department's active status or check for data availability in other time periods."
  }
]



  





