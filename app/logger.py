import logging
import os


os.makedirs("logs", exist_ok=True)


logging.basicConfig(
    filename="logs/application.log",
    level=logging.DEBUG,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )
)


def get_logger(name):
    return logging.getLogger(name)
