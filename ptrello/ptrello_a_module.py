import logging

logger = logging.getLogger("ptrello."+__name__)

def some_function():
    logger.info('a log entry created from a module and called some_function')