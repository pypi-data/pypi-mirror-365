# coding: utf-8
import fnmatch

from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.media_types.finders import (
    MediaTypeFinder as BaseMediaTypeFinder)
from openapi_core.validation.request.validators import (
    RequestValidator as BaseRequestValidator)

from . import utils


class MediaTypeFinder(BaseMediaTypeFinder):
    def find(self, request):
        if request.mimetype in self.content:
            return self.content / request.mimetype, request.mimetype

        for key, value in self.content.items():
            if (
                key in request.mimetype or
                fnmatch.fnmatch(request.mimetype, key)
            ):
                return value, key

        raise MediaTypeNotFound(request.mimetype, list(self.content.keys()))


class RequestValidator(BaseRequestValidator):

    media_type_finder_cls = MediaTypeFinder

    def __init__(
        self, *args, custom_media_type_deserializers=None, **kwargs
    ):
        custom_media_type_deserializers: dict = custom_media_type_deserializers or {}
        custom_media_type_deserializers.update({
            'application/octet-stream': utils.try_decode_csv,
            'multipart/form-data': utils.try_decode_multipart
        })
        super().__init__(
            *args, custom_media_type_deserializers=custom_media_type_deserializers
        )

    def _get_media_type(self, content, request_or_response):
        return self.media_type_finder_cls(content).find(request_or_response)
