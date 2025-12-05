import logging
import sys

from app.core.settings.config import AppSettings


async def setup_logger(app_settings: AppSettings, log_level=logging.INFO):
    """Configures and returns the application's root logger."""
    logger = logging.getLogger(app_settings.logger_name)
    logger.setLevel(log_level)

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger
