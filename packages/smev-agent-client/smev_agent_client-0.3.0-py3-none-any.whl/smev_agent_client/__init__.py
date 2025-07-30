# coding: utf-8

from typing import Union

from .configuration import Config


__config: Union[Config, None] = None


def set_config(config: Config):
    """Установка объекта конфигурации пакета."""

    global __config

    assert isinstance(config, Config)

    __config = config


def get_config() -> Config:
    """Получение установленного объекта конфигурации."""

    global __config

    assert isinstance(__config, Config), 'Не произведена настройка клиента'

    return __config
