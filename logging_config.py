import logging
import os
from logging.handlers import RotatingFileHandler


DEFAULT_LOG_FILE = "/var/log/mcp-human-resources-client/mcp-human-resources-client.log"
DEFAULT_MAX_BYTES = 20 * 1024 * 1024
DEFAULT_BACKUP_COUNT = 10


def _format_bytes(size_in_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_in_bytes)
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    return f"{size:.2f} {units[unit_index]}"


def configure_app_logging() -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    log_file = os.getenv("APP_LOG_FILE", DEFAULT_LOG_FILE)
    max_bytes = int(os.getenv("APP_LOG_MAX_BYTES", DEFAULT_MAX_BYTES))
    backup_count = int(os.getenv("APP_LOG_BACKUP_COUNT", DEFAULT_BACKUP_COUNT))

    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    file_handler.setFormatter(formatter)

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    warning_threshold = int(os.getenv("APP_LOG_WARNING_BYTES", 1 * 1024 * 1024 * 1024))
    try:
        if os.path.isfile(log_file):
            current_size = os.path.getsize(log_file)
            if current_size >= warning_threshold:
                root_logger.warning(
                    "Existing log file is very large before startup (path=%s, size=%s, threshold=%s). "
                    "Consider rotating or truncating this file.",
                    log_file,
                    _format_bytes(current_size),
                    _format_bytes(warning_threshold),
                )
    except Exception as exc:
        root_logger.warning("Failed to check existing log file size: %s", exc)
