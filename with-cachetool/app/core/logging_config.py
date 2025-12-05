import logging
import sys

APPLICATION_LOGGER_NAME = "WithCacheTool"


def setup_logger(log_level=logging.INFO):
    """Configures and returns the application's root logger."""
    logger = logging.getLogger(APPLICATION_LOGGER_NAME)
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
