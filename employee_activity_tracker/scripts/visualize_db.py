# Save as scripts/visualize_db.py
import matplotlib.pyplot as plt
import pandas as pd
import pymysql
import os
import seaborn as sns
from pathlib import Path
from scipy import stats


# Database connection
db = pymysql.connect(
    host=os.getenv("DB_HOST", "mysql"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "123456"),
    database=os.getenv("DB_NAME", "employee_tracking"),
)

# Get data
query = "SELECT * FROM activities"
df = pd.read_sql(query, db)
db.close()

# Create output directory
output_dir = Path("./visualizations")
output_dir.mkdir(exist_ok=True)

# Set style
sns.set(style="whitegrid")

# 1. Department Distribution
plt.figure(figsize=(10, 6))
dept_counts = df["department"].value_counts()
dept_counts.plot(kind="bar", color=sns.color_palette("viridis", len(dept_counts)))
plt.title("Employee Distribution by Department")
plt.xlabel("Department")
plt.ylabel("Number of Records")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(output_dir / "1_department_distribution.png")
print(f"Saved department distribution to {output_dir}/1_department_distribution.png")

# 2. Hours Worked by Employee
plt.figure(figsize=(12, 6))
hours_by_emp = (
    df.groupby("full_name")["hours_worked"].mean().sort_values(ascending=False)
)
hours_by_emp.plot(kind="bar", color=sns.color_palette("magma", len(hours_by_emp)))
plt.title("Average Hours Worked by Employee")
plt.xlabel("Employee")
plt.ylabel("Average Hours")
plt.axhline(y=40, color="r", linestyle="--", label="40 Hour Threshold")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(output_dir / "2_hours_by_employee.png")
print(f"Saved hours by employee to {output_dir}/2_hours_by_employee.png")

# 3. Sales Performance (for Sales department)
plt.figure(figsize=(12, 6))
sales_df = df[df["department"] == "Sales"]
if not sales_df.empty:
    pivot = sales_df.pivot_table(
        index="week_number",
        columns="full_name",
        values="total_sales_rmb",
        aggfunc="sum",
    )
    pivot.plot(marker="o")
    plt.title("Weekly Sales Performance by Employee")
    plt.xlabel("Week Number")
    plt.ylabel("Sales (RMB)")
    plt.grid(True)
    plt.legend(title="Employee")
    plt.tight_layout()
    plt.savefig(output_dir / "3_sales_performance.png")
    print(f"Saved sales performance to {output_dir}/3_sales_performance.png")

# 4. Meetings Distribution
plt.figure(figsize=(10, 6))
meetings = df.groupby(["department", "full_name"])["num_meetings"].sum().unstack(0)
meetings.plot(kind="bar", stacked=True)
plt.title("Total Meetings by Employee and Department")
plt.xlabel("Employee")
plt.ylabel("Number of Meetings")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(output_dir / "4_meetings_distribution.png")
print(f"Saved meetings distribution to {output_dir}/4_meetings_distribution.png")

# 5. Correlation Heatmap
plt.figure(figsize=(8, 6))
numeric_cols = df.select_dtypes(include=["number"]).columns
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Between Numeric Variables")
plt.tight_layout()
plt.savefig(output_dir / "5_correlation_heatmap.png")
print(f"Saved correlation heatmap to {output_dir}/5_correlation_heatmap.png")

print("\nAll visualizations completed!")
