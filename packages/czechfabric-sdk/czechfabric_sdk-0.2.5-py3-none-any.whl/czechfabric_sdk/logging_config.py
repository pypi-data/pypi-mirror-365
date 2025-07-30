import logging

logger = logging.getLogger("czechfabric_sdk")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)
