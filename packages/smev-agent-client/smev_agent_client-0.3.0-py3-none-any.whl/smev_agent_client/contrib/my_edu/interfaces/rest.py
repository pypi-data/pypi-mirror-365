# coding: utf-8
from json import load
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import urlunparse
import logging

from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.spec.shortcuts import create_spec
from requests.models import PreparedRequest
from requests.models import Response
from requests.sessions import Session

from smev_agent_client.interfaces.rest import OpenAPIInterface

from .validation import RequestValidator


logger = logging.getLogger('smev_agent_client')


class OpenAPIInterfaceEmulation(OpenAPIInterface):

    def _send_request(
        self, session: Session, http_request: PreparedRequest, **http_kwargs
    ) -> Response:
        """Эмуляция запроса-ответа.

        Получает запрос, вместо отправки валидирует его.
        Код ответа зависит от успешности валидации.
        """

        openapi_request = RequestsOpenAPIRequest(http_request)

        # Из URL удаляется мнемоника агента и basePath спцификации, т.к.
        # это не учитывается в спецификации и поэтому запрос не проходит валидацию
        parsed_urlpattern = urlparse(openapi_request.full_url_pattern)
        scheme, netloc, path, params, query, fragment = parsed_urlpattern
        path = ''.join(f'/{part}' for part in path.split('/')[3:])
        openapi_request.full_url_pattern = urlunparse((
            scheme, netloc, path, params, query, fragment
        ))

        validator = self._get_request_validator()

        result = validator.validate(openapi_request)

        response = Response()

        assert http_request.url
        response.url = http_request.url

        if result.errors:
            logger.error('; '.join(str(err) for err in result.errors))
            response.status_code = 400
        else:
            logger.info('Запрос прошел валидацию')
            response.status_code = 200

        return response

    def _get_request_validator(self):
        with Path(__file__).parent.joinpath('myedu.json').open('r') as spec_file:
            spec_dict = load(spec_file)

        return RequestValidator(create_spec(spec_dict))
