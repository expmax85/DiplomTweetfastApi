import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler(filename='logs/unexpected_error.log', mode='a')
handler.setLevel(logging.ERROR)
fmt = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(fmt)
logger.addHandler(handler)
