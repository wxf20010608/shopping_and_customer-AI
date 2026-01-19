#!/bin/sh
set -e

# 等待 backend 服务可用（通过 DNS 解析和端口检查）
echo "Waiting for backend service to be available..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
  # 尝试 DNS 解析和端口检查
  if nslookup backend > /dev/null 2>&1 && nc -z backend 8000 > /dev/null 2>&1; then
    echo "Backend service is available, starting nginx..."
    break
  fi
  attempt=$((attempt + 1))
  if [ $((attempt % 5)) -eq 0 ]; then
    echo "Backend service not ready, waiting... (attempt $attempt/$max_attempts)"
  fi
  sleep 1
done

if [ $attempt -eq $max_attempts ]; then
  echo "Warning: Backend service not found after $max_attempts attempts, starting nginx anyway..."
fi

# 执行 nginx 的默认启动命令
exec nginx -g "daemon off;"
