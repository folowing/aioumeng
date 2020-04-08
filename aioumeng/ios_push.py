import datetime
import json

from .common import PushType
from .exception import (
    AioUMengPushError,
    AioUMengPushParamsError,
)


class IOSPushNotification:

    def __init__(self, title=None, subtitle=None, body=None, badge=None,
                 sound=None,
                 extra=None):
        self.title = title
        self.subtitle = subtitle
        self.body = body
        self.badge = badge
        self.sound = sound
        self.extra = extra

    @classmethod
    def create(cls, title, subtitle, body, badge=1, sound='default',
               extra=None):
        return cls(title=title, subtitle=subtitle, body=body, badge=badge,
                   sound=sound, extra=extra)

    def to_dto(self):
        aps = {
            'alert': {
                'title': self.title,
                'subtitle': self.subtitle,
                'body': self.body
            },
            'badge': self.badge,
            'sound': self.sound,
        }
        result = {
            'aps': aps,
        }
        if self.extra:
            result.update(self.extra)
        return result


class IOSPushPolicy:

    def __init__(self, start_time=None, expire_time=None,
                 out_biz_no=None, apns_collapse_id=None):
        """
        :param start_time: datetime
        :param expire_time: datetime
        :param out_biz_no: string
        :param apns_collapse_id: string
        """
        self.start_time = start_time
        self.expire_time = expire_time
        self.out_biz_no = out_biz_no
        self.apns_collapse_id = apns_collapse_id

    @classmethod
    def create(cls, start_time=None, expire_time=None,
               out_biz_no=None, apns_collapse_id=None):

        if start_time and expire_time and expire_time < start_time:
            raise AioUMengPushParamsError('expire time must after start time')

        return cls(start_time=start_time, expire_time=expire_time,
                   out_biz_no=out_biz_no, apns_collapse_id=apns_collapse_id)

    def to_dto(self):
        result = {}
        if self.start_time:
            result['start_time'] = self.start_time.strftime(
                'yyyy-MM-dd HH:mm:ss')
        if self.expire_time:
            result['expire_time'] = self.expire_time.strftime(
                'yyyy-MM-dd HH:mm:ss')
        if self.out_biz_no:
            result['out_biz_no'] = self.out_biz_no
        if self.apns_collapse_id:
            result['apns_collapse_id'] = self.apns_collapse_id
        return result


class IOSPush:

    async def single_push_ios(self, device_token, msg, description,
                              policy=None):
        """
        :param device_token: string
        :param msg: IOSPushNotification
        :param policy: IOSPushPolicy
        :param description: string
        :return:
        """
        if not self.ios_push_config:
            raise AioUMengPushError('ios push config not set')

        post_body = {
            'appkey': self.ios_push_config.key,
            'timestamp': str(int(datetime.datetime.now().timestamp())),
            'type': PushType.UNI_CAST,
            'device_tokens': device_token,
            'payload': msg.to_dto(),
            'production_mode': self.ios_push_config.production_mode,
            'description': description,
        }
        if policy:
            post_body['policy'] = policy.to_dto()

        body = json.dumps(post_body, ensure_ascii=False, separators=(',', ':'),
                          sort_keys=True)
        print(body)

        method = 'POST'
        sign = self._get_sign(method, self.GATEWAY, body,
                              self.ios_push_config.secret)

        # print(sign)
        result = await self._do_request(method, self.GATEWAY, body,
                                        {'sign': sign})
        return result
