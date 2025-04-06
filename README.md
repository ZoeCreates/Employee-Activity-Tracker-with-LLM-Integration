# 🧠 Employee Activity Tracker with LLM Integration

A full-stack system to **track**, **visualize**, and **query** employee activity data using **natural language** powered by DeepSeek LLM. Includes automated visual dashboards and smart SQL generation — all containerized with Docker.

---

## 🚀 Features

- 📊 **Data Visualization** – Generate insightful charts on department distribution, working hours, sales trends, meeting counts, and correlations
- 🤖 **LLM Integration** – Ask natural language questions like “Who worked overtime last week?” and receive accurate, human-readable answers
- 🐳 **Dockerized** – Run both the backend and MySQL in containers using Docker Compose

---

## 🗂️ Project Structure

```bash
employee_activity_tracker/
├── scripts/
│   ├── llm_integration.py        # Natural language query → SQL → Result → Explanation
│   ├── populate_data.py          # Insert sample employee activity records
│   ├── visualize_db.py           # Generate charts using Matplotlib & Seaborn
│   ├── init_db.sql               # MySQL schema setup
│   ├── benchmark_results.json    # LLM query output results
│   └── visualizations/           # Output chart images (.png)
├── mysql_data/                   # MySQL data volume (auto-managed)
├── docker-compose.yml            # Docker setup for app + MySQL
├── requirements.txt              # Python dependencies
├── .env.template                 # Sample environment config
└── .gitignore
⚙️ Environment Setup
1. Clone the repo
bash
复制
编辑
git clone https://github.com/YOUR_USERNAME/employee-activity-tracker.git
cd employee-activity-tracker
2. Set up environment variables
Create a .env file from the template:

bash
复制
编辑
cp .env.template .env
Edit .env and fill in your API key:

env
复制
编辑
DB_HOST=mysql
DB_USER=root
DB_PASSWORD=123456
DB_NAME=employee_tracking

DEEPSEEK_API_KEY=your-deepseek-api-key-here
⚠️ Never commit .env to GitHub

3. Start services using Docker
bash
复制
编辑
docker-compose up -d
This will spin up:

🗄️ MySQL container (mysql_dev)

🐍 Python app container (app, with working directory /app/scripts)

📊 How to Use the System
Step 1: Populate the Database
bash
复制
编辑
docker-compose exec app python populate_data.py
Step 2: Generate Visual Charts
bash
复制
编辑
docker-compose exec app python visualize_db.py
Charts will be saved to: scripts/visualizations/

Step 3: Run LLM Benchmark Queries
bash
复制
编辑
docker-compose exec app python llm_integration.py
LLM results will be saved to: benchmark_results.json

