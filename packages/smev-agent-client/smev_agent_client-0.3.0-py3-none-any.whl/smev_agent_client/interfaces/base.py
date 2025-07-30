# coding: utf-8
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .configuration import Config  # noqa
    from ..logging.base import AbstractLogger  # noqa


class AbstractInterface(ABC):

    _config: 'Config'
    _logger: 'AbstractLogger'

    def __init__(
        self, config: 'Config', logger: 'AbstractLogger'
    ):
        self._config = config
        self._logger = logger

    @abstractmethod
    def send(self, request):
        """Отправляет запрос и возвращает результат отправки запроса."""
