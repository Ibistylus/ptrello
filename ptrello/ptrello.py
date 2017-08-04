# -*- coding: utf-8 -*-

"""Main module."""
import logging
from core.config import settings
from core.config import logger

import ptrello_a_module

logger = logging.getLogger("ptrello."+__name__)


def sample_function():
    logger.info("sample_function ran")


def main():
    logger.debug("Prior to configuration")
    sample_function()
    ptrello_a_module.some_function()


if __name__ == '__main__':  
    main()