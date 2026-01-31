#!/usr/bin/env python3
"""
后端启动脚本 - 用于宝塔/生产环境
必须从 backend 目录运行: cd /www/wwwroot/backend && python run.py
或: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
