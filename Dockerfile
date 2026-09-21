FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    DECISION_DB=/app/data/decision.db

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝应用代码
COPY app ./app

# SQLite 数据目录（Compose 中挂载卷持久化）
RUN mkdir -p /app/data

EXPOSE 8000

# 健康检查：供 docker compose 的 depends_on（service_healthy）等启动依赖使用。
# 用镜像内自带的 Python 探测 HTTP 端口，无需额外安装 curl。
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/', timeout=2).status == 200 else 1)"

# 启动时自动建库建表（见 app/main.py 的 lifespan）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
