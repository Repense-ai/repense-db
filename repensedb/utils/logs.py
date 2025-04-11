import logging

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LOGGING_CONFIG = {
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "level": logging.INFO,
    "datefmt": DATE_FORMAT,
}
