import logging
import sys

from src.settings.base import base_settings


def prepare_logging():
    logger = logging.getLogger()
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(
        logging.Formatter("%(asctime)s:%(name)s:%(levelname)s %(message)s", "%Y%m%d %H:%M:%S")
    )

    logger.handlers.clear()
    logger.addHandler(log_handler)
    logger.setLevel(getattr(logging, base_settings.LOG_LEVEL.upper()))

    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = []
    uvicorn_access_logger.propagate = False
    uvicorn_access_logger.addHandler(log_handler)

    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.handlers = []
    uvicorn_error_logger.propagate = False
    uvicorn_error_logger.addHandler(log_handler)

    # reinitialize all exist loggers
    for name in logging.root.manager.loggerDict:
        _ = logging.getLogger(name)
