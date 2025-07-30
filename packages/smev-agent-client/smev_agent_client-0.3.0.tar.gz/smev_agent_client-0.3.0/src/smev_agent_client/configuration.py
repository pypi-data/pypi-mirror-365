# coding: utf-8
from typing import TYPE_CHECKING

from pydantic.fields import Field

from .const import DEFAULT_REQUEST_RETRIES
from .const import DEFAULT_REQUEST_TIMEOUT
from .const import DEFAULT_RETRY_FACTOR


if TYPE_CHECKING:
    from dataclasses import dataclass  # noqa
else:
    from pydantic.dataclasses import dataclass  # noqa


@dataclass
class Config:

    """Объект конфигурации пакета."""

    agent_url: str = Field(
        title='Адрес Агента Поставщика данных (schema://host:post)',
        default='http://localhost:8090',
        min_length=1
    )
    system_mnemonics: str = Field(
        title='Мнемоника Агента Поставщика данных',
        min_length=1
    )
    request_retries: int = Field(
        title='Количество повторных попыток',
        default=DEFAULT_REQUEST_RETRIES
    )
    retry_factor: int = Field(
        title='Шаг увеличения задержки м.д. запросами',
        default=DEFAULT_RETRY_FACTOR
    )
    timeout: int = Field(
        title='Таймаут запроса, сек',
        default=DEFAULT_REQUEST_TIMEOUT
    )
    interface: str = 'smev_agent_client.interfaces.rest.OpenAPIInterface'
    logger: str = 'smev_agent_client.logging.db.Logger'
