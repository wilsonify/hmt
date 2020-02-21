import json
import os
import shutil
from unittest.mock import patch

from http_types import Response, Request

from meeshkan import UpdateMode
from meeshkan.server.utils.data_callback import RequestLoggingCallback


def test_request_logging():
    if os.path.exists('./tests/tmp'):
        shutil.rmtree('./tests/tmp')

    request = Request(method='get',
                      host='another.api.com',
                      pathname='/echo',
                      query={'message': 'Hello'},
                      body='',
                      bodyAsJson={},
                      protocol='http',
                      headers={})
    response = Response(statusCode=200, body='{"message": "hello"}', bodyAsJson={"message": "hello"},
                        headers={})

    with RequestLoggingCallback(log_dir='./tests/tmp/logs', specs_dir='./tests/tmp/specs',
                                update_mode=UpdateMode.MIXED) as data_callback:
        data_callback.log(request, response)

    assert os.path.exists('./tests/tmp/logs/another.api.com.jsonl')
    assert os.path.exists('./tests/tmp/specs/another.api.com_mixed.yaml')

    request = Request(method='get',
                      host='api.com',
                      pathname='/echo',
                      query={'message': 'Hello'},
                      body='',
                      bodyAsJson={},
                      protocol='http',
                      headers={})
    response = Response(statusCode=200, body='{"message": "hello"}', bodyAsJson={"message": "hello"},
                        headers={})

    with RequestLoggingCallback(log_dir='./tests/tmp/logs', specs_dir='./tests/tmp/specs',
                                update_mode=UpdateMode.GEN) as data_callback:
        data_callback.log(request, response)

    assert os.path.exists('./tests/tmp/logs/api.com.jsonl')
    assert os.path.exists('./tests/tmp/specs/api.com_gen.yaml')

    with open('./tests/tmp/logs/api.com.jsonl', 'r') as f:
        data = f.readlines()
        assert 1 == len(data)
        http_exchange = json.loads(data[0])
        assert request == http_exchange['request']
        assert response == http_exchange['response']


    shutil.rmtree('./tests/tmp')

    with RequestLoggingCallback(log_dir='./tests/tmp/logs', specs_dir='./tests/tmp/specs',
                                update_mode=None) as data_callback:
        data_callback.log(request, response)

    assert os.path.exists('./tests/tmp/logs/api.com.jsonl')
    assert 0 == len(os.listdir('./tests/tmp/specs'))


    shutil.rmtree('./tests/tmp')