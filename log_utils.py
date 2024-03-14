import logging

LOGGER = logging.getLogger("Event Inclusion Check Script")


def set_logging_config():
    logger = LOGGER
    logger.setLevel(logging.INFO)

    # color
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
