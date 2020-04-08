import asyncio
import hashlib
import json
import logging

import aiohttp

from .android_push import AndroidPush
from .exception import (
    AioUMengPushTimeoutError,
    AioUMengPushError,
)
from .ios_push import IOSPush

logger = logging.getLogger('umengpush')


class PushConfig:
    def __init__(self, key, secret, production_mode):
        self.key = key
        self.secret = secret
        self.production_mode = production_mode


class AioUMengPush(AndroidPush, IOSPush):
    def __init__(self, android_push_config, ios_push_config, timeout=30):
        """
        :param android_push_config: PushConfig
        :param ios_push_config: PushConfig
        :param timeout:
        """
        self.android_push_config = android_push_config
        self.ios_push_config = ios_push_config
        self.timeout = timeout

        conn = aiohttp.TCPConnector(limit=1024)
        self._session = aiohttp.ClientSession(
            connector=conn,
            skip_auto_headers={'Content-Type'},
        )

    def __del__(self):
        if not self._session.closed:
            if self._session._connector is not None \
                    and self._session._connector_owner:
                self._session._connector.close()
            self._session._connector = None

    GATEWAY = 'https://msgapi.umeng.com/api/send'

    async def _do_request(self, method, url, body, params=None,
                          content_type=None):
        headers = {
            'connection': 'keep-alive',
            'content-type': 'application/json',
        }
        if content_type:
            headers['content-type'] = content_type

        try:
            async with self._session.request(method, url, data=body,
                                             params=params,
                                             headers=headers,
                                             timeout=self.timeout) as aio_resp:

                text = await aio_resp.text()
                json_result = json.loads(text)
                return json_result

        except asyncio.TimeoutError:
            raise AioUMengPushTimeoutError(
                "Connection to umeng push gateway timed out.")
        except Exception as e:
            logger.exception('aioumengpush error')
            raise AioUMengPushError(e)

    def _get_sign(self, method, url, body, secret):
        s = f'{method}{url}{body}{secret}'
        m = hashlib.md5(s.encode())
        return m.hexdigest()
