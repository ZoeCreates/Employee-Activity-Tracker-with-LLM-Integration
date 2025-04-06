# # Dockerfile
# FROM python:3.9-slim

# WORKDIR /app

# # 复制依赖文件并安装
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # 复制项目代码
# COPY . .

# CMD ["tail", "-f", "/dev/null"]  # 保持容器运行


# 正确示例（注意反斜杠和 && 的用法）
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖（必须写成单条RUN）
RUN apt-get update && \
    apt-get install -y coreutils && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 保持容器运行的命令
CMD ["sh", "-c", "while true; do sleep 86400; done"]