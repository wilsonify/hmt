import json
import logging
import os
from urllib import parse
from typing import cast

from http_types import RequestBuilder, Request, HttpMethod
# from ..utils.http_utils import split_path
from tornado.web import RequestHandler

logger = logging.getLogger(__name__)


class MockServerView(RequestHandler):
    SUPPORTED_METHODS = ["GET", "POST", "HEAD", "DELETE", "PATCH", "PUT", "OPTIONS"]

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def get(self, **kwargs):
        self._serve()

    def post(self):
        self._serve()

    def head(self, **kwargs):
        self._serve()

    def delete(self, **kwargs):
        self._serve()

    def patch(self, **kwargs):
        self._serve()

    def put(self, **kwargs):
        self._serve()

    def options(self, **kwargs):
        self._serve()

    def _serve(self):
        query = parse.parse_qs(self.request.query)

        fullpath = "{}?{}".format(self.request.path, self.request.query) if query else self.request.path
                # ignoring type due to this error
        '''
          46:34 - error: Argument of type 'str' cannot be assigned to parameter 'method' of type 'Literal['connect', 'head', 'trace', 'options', 'delete', 'patch', 'post', 'put', 'get']'
          'str' cannot be assigned to 'Literal['connect']'
          'str' cannot be assigned to 'Literal['head']'
          'str' cannot be assigned to 'Literal['trace']'
          'str' cannot be assigned to 'Literal['options']'
          'str' cannot be assigned to 'Literal['delete']'
        '''
        request = Request(method=cast(HttpMethod, self.request.method.lower()), # type: ignore
                                  host=self.request.host,
                                  path=fullpath,
                                  pathname=self.request.path,
                                  protocol=self.request.protocol,
                                  query=query,
                                  body=self.request.body,
                                  bodyAsJson=self._extract_json_safely(self.request.body),
                                  headers={k:v for k,v in self.request.headers.get_all()})
        RequestBuilder.validate(request)


        response = self.application.mocking_service.match(request)
        self.write(response['body'])

    def _extract_json_safely(self, text):
        if text:
            try:
                return json.loads(text)
            except Exception as e:
                pass

        return {}

