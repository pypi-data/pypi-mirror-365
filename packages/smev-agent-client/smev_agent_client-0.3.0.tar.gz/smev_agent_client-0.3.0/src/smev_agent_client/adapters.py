# coding: utf-8

from typing import TYPE_CHECKING

from .utils import import_string


if TYPE_CHECKING:
    from ..configuration import Config  # noqa
    from .logging.base import AbstractLogger  # noqa
    from .interfaces import AbstractInterface  # noqa


class AgentAdapter:

    _config: 'Config'
    _interface: 'AbstractInterface'
    _logger: 'AbstractLogger'

    def __init__(self):
        self._config = None
        self._load_config()

    def _load_config(self) -> 'Config':
        from smev_agent_client import get_config

        set_config = get_config()

        if self._config is not set_config:
            self._config = set_config

        self._logger = import_string(self._config.logger)()
        self._interface = import_string(
            self._config.interface
        )(
            self._config, self._logger
        )

        return self._config

    def send(self, request):
        """Отправка запроса."""
        return self._interface.send(request)


adapter = AgentAdapter()
