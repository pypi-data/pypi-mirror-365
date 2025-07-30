import json
import logging
import os
import traceback
from datetime import datetime, timedelta, timezone

from .config import Config


class StructuredLogFormatter(logging.Formatter):
    """结构化JSON日志格式化器"""

    def __init__(self, system: str = "default_system", stage: str = "default_stage"):
        super().__init__()
        self.system = system
        self.stage = stage

    def format(self, record: logging.LogRecord) -> str:
        # 提取事件类型和堆栈信息
        event = getattr(record, "event", "unknown_event")
        stack_trace = getattr(record, "stack_trace", None)

        if record.levelno == logging.ERROR and record.exc_info:
            exc_type, _, exc_tb = record.exc_info
            event = exc_type.__name__
            stack_trace = self._format_exception(exc_tb)

        # 构建日志结构体
        log_data = {
            "thread_id": record.thread,
            "thread_name": record.threadName,
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "system": getattr(record, "system", self.system),
            "stage": getattr(record, "stage", self.stage),
            "event": event,
            "message": record.getMessage(),
            "caller": {
                "module": record.module,
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            },
            "duration_ms": getattr(record, "duration_ms", None),
            "stack_trace": stack_trace,
        }

        return json.dumps(
            {k: v for k, v in log_data.items() if v is not None}, ensure_ascii=False, default=self._json_serializer
        )

    def _json_serializer(self, obj):
        """JSON序列化钩子函数"""
        if isinstance(obj, (datetime, timedelta)):
            return str(obj)
        if hasattr(obj, "__dict__"):
            return vars(obj)
        return f"<不可序列化对象: {type(obj).__name__}>"

    def _format_exception(self, tb):
        """格式化异常堆栈"""
        return "".join(traceback.format_tb(tb))


def setup_logger(
    system: str = "default_system",
    stage: str = "default_stage",
) -> logging.Logger:
    """
    初始化日志系统
    Args:
        system: 系统标识
        stage: 阶段标识
        log_file_path: 日志文件路径
        debug_mode: 是否调试模式
    Returns:
        配置完成的日志记录器
    """
    logger = logging.getLogger(system)
    logger.setLevel(logging.DEBUG if Config.DEBUG else logging.INFO)

    if not logger.handlers:
        # 创建格式化器
        formatter = StructuredLogFormatter(system=system, stage=stage)

        # 控制台处理器
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # 文件处理器（如果提供路径）
        if Config.LOG_PATH:
            os.makedirs(os.path.dirname(Config.LOG_PATH), exist_ok=True)
            fh = logging.FileHandler(Config.LOG_PATH, encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)

    return logger
