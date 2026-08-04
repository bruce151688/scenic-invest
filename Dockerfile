FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY backend/ ./backend/
COPY frontend/dist/ ./frontend/dist/
COPY data/ ./data/

# 创建数据目录
RUN mkdir -p /var/data

WORKDIR /app/backend

# 启动命令
CMD uvicorn render_app:app --host 0.0.0.0 --port ${PORT:-8000}
