FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 配置 Debian 镜像源（使用阿里云镜像，解决网络连接问题）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    (echo "deb http://mirrors.aliyun.com/debian/ bookworm main" > /etc/apt/sources.list && \
     echo "deb http://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list && \
     echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main" >> /etc/apt/sources.list)

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
# 创建 pip 配置文件，使用镜像源
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "index-url = https://mirrors.aliyun.com/pypi/simple/" >> /root/.pip/pip.conf && \
    echo "trusted-host = mirrors.aliyun.com" >> /root/.pip/pip.conf && \
    echo "timeout = 1000" >> /root/.pip/pip.conf && \
    echo "retries = 5" >> /root/.pip/pip.conf && \
    echo "no-cache-dir = true" >> /root/.pip/pip.conf
# 安装依赖，如果哈希检查失败则尝试官方源
RUN pip install --no-cache-dir --default-timeout=1000 --retries=5 -r /app/requirements.txt || \
    (echo "镜像源安装失败（可能是哈希检查问题），尝试官方源..." && \
     pip install --no-cache-dir --default-timeout=1000 --retries=5 -i https://pypi.org/simple/ -r /app/requirements.txt)

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
