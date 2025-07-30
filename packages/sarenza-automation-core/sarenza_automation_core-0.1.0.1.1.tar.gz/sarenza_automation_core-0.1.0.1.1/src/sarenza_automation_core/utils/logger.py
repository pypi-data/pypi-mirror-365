# your_project/utils/logger_config.py
import sys
from loguru import logger
from datetime import datetime
import os


def setup_loguru(log_dir="logs", log_level="INFO"):
    """
    Configures Loguru for a test automation framework, suitable for CI/CD.
    """
    logger.remove()

    # --- Console Output ---
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # --- File Output ---
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(log_dir, f"automation_test_{timestamp}.log")
    error_log_file_path = os.path.join(
        log_dir, f"automation_test_errors_{timestamp}.log"
    )

    logger.add(
        log_file_path,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {thread.name: <15} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        compression="zip",
        retention="7 days",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    logger.add(
        error_log_file_path,
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {thread.name: <15} | {name}:{function}:{line} - {message}",
        rotation="5 MB",
        compression="zip",
        retention="3 days",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    logger.add(
        lambda msg: logger.warning(msg),
        format="{message}",
        level="WARNING",
        filter=lambda record: record["name"] == "py.warnings",
    )

    logger.info(
        f"Loguru configured. Detailed logs in '{log_file_path}' (level: {log_level}). Error logs in '{error_log_file_path}'."
    )
