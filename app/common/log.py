import logging
import sys


def get_logger():
    """
    Get Logger
    @return: 
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    streamHandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    return logger
