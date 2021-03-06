import json
import msgpack
import requests


class JsonRpcClient(object):

    codec = json
    mimetype = "application/json"

    def __init__(self, endpoint=None):
        self._id = 1
        self._endpoint = endpoint
        self._session = requests.Session()

    def __getattr__(self, method):
        # assert self._endpoint is not None

        def call(**kwargs):
            return self._session.post(
                self._endpoint,
                data=self.codec.dumps(self.request(method, **kwargs)),
                headers={"Content-Type": self.mimetype})
        return call

    def call(self, method, **kwargs):
        return getattr(self, method)(**kwargs)

    def request(self, method, **kwargs):
        req = dict(
            method=method,
            id=str(self._id),
            jsonrpc='2.0',
            params=kwargs,
        )
        return req

    @staticmethod
    def response(resp):
        if 'result' in resp:
            return resp['result']
        elif 'result' not in resp and resp['error'].get('data') is None:
            return None

        if 'error' not in resp:
            raise Exception('invalid JSON-RPC protocol: missing error')

        raise Exception('{}:\n{}'.format(
            resp['error']['message'],
            str(resp['error'].get('data', ''))))


class MsgpackRpcClient(JsonRpcClient):
    codec = msgpack
    mimetype = "application/x-msgpack"
