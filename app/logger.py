import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

os.makedirs(LOG_DIR, exist_ok=True)

TEN_MB = 10*1024*1024

file_handler = RotatingFileHandler(
    filename=LOG_FILE,
    maxBytes=TEN_MB,
    backupCount=5,
    encoding="utf-8"
)

log_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(log_formatter)

# Also output logs to terminal console for local debugging
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Get root logger
logger = logging.getLogger("taiga_tower")
logger.setLevel(logging.INFO)

# Avoid duplicate handlers if re-imported
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
