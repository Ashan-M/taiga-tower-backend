import logging
import sys

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
# changed the logger from file to this following for vercel

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
