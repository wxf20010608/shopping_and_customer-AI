"""
日志查看服务
用于读取和管理日志文件
"""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import os


class LogService:
    """日志查看服务类"""
    
    def __init__(self):
        self.log_dir = self._get_log_dir()
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_log_dir(self) -> Path:
        """获取日志目录"""
        log_dir_env = os.environ.get("LOG_DIR")
        if log_dir_env:
            return Path(log_dir_env)
        
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        return BASE_DIR / "logs"
    
    def list_log_files(self) -> List[Dict]:
        """列出所有日志文件"""
        log_files = []
        
        # 主要日志文件
        main_log = self.log_dir / "app.log"
        if main_log.exists():
            stat = main_log.stat()
            log_files.append({
                "name": "app.log",
                "path": str(main_log),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": "main"
            })
        
        # 错误日志文件
        error_log = self.log_dir / "error.log"
        if error_log.exists():
            stat = error_log.stat()
            log_files.append({
                "name": "error.log",
                "path": str(error_log),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": "error"
            })
        
        # 轮转的日志文件（按日期）
        for log_file in sorted(self.log_dir.glob("*.log.*"), reverse=True):
            if log_file.is_file():
                stat = log_file.stat()
                log_files.append({
                    "name": log_file.name,
                    "path": str(log_file),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "type": "rotated"
                })
        
        return log_files
    
    def read_log_file(
        self, 
        filename: str, 
        lines: int = 1000,
        level_filter: Optional[str] = None,
        search_text: Optional[str] = None,
        reverse: bool = True
    ) -> Dict:
        """读取日志文件内容
        
        Args:
            filename: 日志文件名
            lines: 读取的行数（默认1000行，从文件末尾读取）
            level_filter: 日志级别过滤（DEBUG, INFO, WARNING, ERROR, CRITICAL）
            search_text: 搜索文本（在日志行中搜索）
            reverse: 是否反向读取（从文件末尾开始）
        
        Returns:
            包含日志内容的字典
        """
        log_file = self.log_dir / filename
        
        # 安全检查：确保文件在日志目录内
        if not log_file.resolve().is_relative_to(self.log_dir.resolve()):
            raise ValueError(f"非法文件路径: {filename}")
        
        if not log_file.exists():
            return {
                "filename": filename,
                "total_lines": 0,
                "lines": [],
                "error": "日志文件不存在"
            }
        
        try:
            # 读取文件内容
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
            
            total_lines = len(all_lines)
            
            # 应用过滤器
            filtered_lines = all_lines
            if level_filter:
                level_upper = level_filter.upper()
                filtered_lines = [
                    line for line in filtered_lines 
                    if f" - {level_upper} - " in line or f" - {level_upper} -" in line
                ]
            
            if search_text:
                search_lower = search_text.lower()
                filtered_lines = [
                    line for line in filtered_lines
                    if search_lower in line.lower()
                ]
            
            # 取最后 N 行（如果 reverse=True）
            if reverse:
                filtered_lines = filtered_lines[-lines:] if len(filtered_lines) > lines else filtered_lines
            else:
                filtered_lines = filtered_lines[:lines] if len(filtered_lines) > lines else filtered_lines
            
            return {
                "filename": filename,
                "total_lines": total_lines,
                "filtered_lines": len(filtered_lines),
                "lines": [line.rstrip('\n\r') for line in filtered_lines],
                "level_filter": level_filter,
                "search_text": search_text
            }
        except Exception as e:
            return {
                "filename": filename,
                "total_lines": 0,
                "lines": [],
                "error": str(e)
            }
    
    def get_log_stats(self) -> Dict:
        """获取日志统计信息"""
        log_files = self.list_log_files()
        
        total_size = sum(f["size"] for f in log_files)
        
        return {
            "log_dir": str(self.log_dir),
            "total_files": len(log_files),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files": log_files
        }
    
    def clear_log_file(self, filename: str) -> Dict:
        """清空日志文件（保留文件但清空内容）"""
        log_file = self.log_dir / filename
        
        # 安全检查
        if not log_file.resolve().is_relative_to(self.log_dir.resolve()):
            raise ValueError(f"非法文件路径: {filename}")
        
        if not log_file.exists():
            return {"status": "error", "message": "日志文件不存在"}
        
        try:
            # 清空文件内容
            log_file.write_text("", encoding='utf-8')
            return {"status": "ok", "message": f"日志文件 {filename} 已清空"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# 全局服务实例
_log_service = None


def get_log_service() -> LogService:
    """获取日志查看服务实例（单例模式）"""
    global _log_service
    if _log_service is None:
        _log_service = LogService()
    return _log_service
