# coding: utf-8

import logging

from .base import AbstractLogger
from .base import Entry


class Logger(AbstractLogger):

    def __init__(self):
        self.__logger = logging.getLogger('smev_agent_client')

    def log(self, entry: Entry) -> None:

        assert isinstance(entry, Entry)

        if entry.error:
            method = self.__logger.error
        else:
            method = self.__logger.info

        method(str(entry))
