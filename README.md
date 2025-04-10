
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


## Example LLM Q#A Benchmark Test


<img width="1440" alt="Screenshot 2025-04-09 at 11 58 08 PM" src="https://github.com/user-attachments/assets/04edcd5f-443d-45d5-8582-a492745ae5f5" />



  





