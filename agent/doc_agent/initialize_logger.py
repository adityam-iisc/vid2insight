import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Optional: Add handler if not already added
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
