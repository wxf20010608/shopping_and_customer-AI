"""
日志配置模块
配置日志记录到文件，支持轮转和不同级别
"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


def setup_logging(log_dir: Optional[str] = None, log_level: str = "INFO"):
    """配置日志记录到文件
    
    Args:
        log_dir: 日志文件目录，如果为 None，则使用默认目录（backend/logs）
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    """
    # 确定日志目录
    if log_dir is None:
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        log_dir = BASE_DIR / "logs"
    else:
        log_dir = Path(log_dir)
    
    # 创建日志目录
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 清除已有的处理器
    root_logger.handlers.clear()
    
    # 创建格式器
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（所有日志）- 按日期轮转，保留30天
    log_file = log_dir / "app.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_file),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # 错误日志文件（只记录 ERROR 及以上级别）
    error_log_file = log_dir / "error.log"
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(error_log_file),
        when='midnight',
        interval=1,
        backupCount=90,  # 错误日志保留更久
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # 控制台处理器（可选，用于开发环境）
    if os.environ.get("LOG_TO_CONSOLE", "true").lower() == "true":
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # 记录日志配置完成
    root_logger.info(f"日志系统已初始化，日志目录: {log_dir}")
    
    return log_dir


def get_log_dir() -> Path:
    """获取日志目录路径"""
    log_dir_env = os.environ.get("LOG_DIR")
    if log_dir_env:
        return Path(log_dir_env)
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    return BASE_DIR / "logs"
