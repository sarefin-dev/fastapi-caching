import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):  # copied from google ai (search)
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

        #return super().emit(record)


async def setup_logging():
    logging.getLogger().handlers = [InterceptHandler()]

    for name in logging.root.manager.loggerDict:
        std_logger = logging.getLogger(name)
        if isinstance(std_logger, logging.Logger):
            std_logger.propagate = False
    
    logger.remove()
        

    LOGURU_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<cyan>{name}</cyan> | "
        "<level>{level}</level> | "
        "<cyan>{module}</cyan>:<cyan>{line}</cyan> | "
        "{message}"
    )

    logger.add("log.log", rotation="2 MB", compression="zip", level="INFO")
    logger.add(sys.stderr, format=LOGURU_FORMAT, level="INFO")
