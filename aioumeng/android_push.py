import datetime
import json
import re

from .common import (
    PushType,
    DisplayType,
    AfterOpenType,
)
from .exception import (
    AioUMengPushError,
    AioUMengPushParamsError,
)

URL_PATTER = re.compile(r'https?://')


class AndroidPushNotification:

    def __init__(self, ticker=None, title=None, text=None,
                 icon=None, large_icon=None,
                 img=None, sound=None, builder_id=None,
                 play_vibrate=None, play_lights=None, play_sound=None,
                 after_open=None, url=None, activity=None, custom=None,
                 extra=None,
                 ):
        self.ticker = ticker
        self.title = title
        self.text = text

        self.icon = icon
        self.large_icon = large_icon
        self.img = img

        self.sound = sound

        self.builder_id = builder_id

        self.play_vibrate = play_vibrate
        self.play_lights = play_lights
        self.play_sound = play_sound

        self.after_open = after_open
        self.url = url
        self.activity = activity
        self.custom = custom

        self.extra = extra

    @classmethod
    def create(cls, ticker, title, text, icon=None, large_icon=None,
               img=None, sound=None, builder_id=0,
               play_vibrate=True, play_lights=True, play_sound=True,
               after_open=AfterOpenType.GO_APP, url=None, activity=None,
               custom=None, extra=None):
        if not ticker:
            raise AioUMengPushParamsError('ticker is required')

        if not title:
            raise AioUMengPushParamsError('title is required')

        if not text:
            raise AioUMengPushParamsError('text is required')

        if icon and not icon.startswith('R.drawable.'):
            raise AioUMengPushParamsError('icon name error')

        if large_icon and not large_icon.startswith('R.drawable.'):
            raise AioUMengPushParamsError('large icon name error')

        if img and not URL_PATTER.match(img):
            raise AioUMengPushParamsError('img url error')

        if sound and not icon.startswith('R.raw.'):
            raise AioUMengPushParamsError('sound name error')

        if after_open:
            if after_open == AfterOpenType.GO_URL:
                if not URL_PATTER.match(url):
                    raise AioUMengPushParamsError(
                        'url is required when go_url after open')
            elif after_open == AfterOpenType.GO_ACTIVITY:
                if not activity:
                    raise AioUMengPushParamsError(
                        'activity is required when go_activity after open')
            elif after_open == AfterOpenType.GO_CUSTOM:
                if not custom:
                    raise AioUMengPushParamsError(
                        'custom is required when go_custom after open')

        return cls(ticker=ticker, title=title, text=text,
                   icon=icon, large_icon=large_icon, img=img, sound=sound,
                   builder_id=builder_id, play_vibrate=play_vibrate,
                   play_lights=play_lights, play_sound=play_sound,
                   after_open=after_open, url=url, activity=activity,
                   custom=custom, extra=extra)

    def to_dto(self):
        body = {
            'ticker': self.ticker,
            'title': self.title,
            'text': self.text,
            'play_vibrate': self.play_vibrate and 'true' or 'false',
            'play_lights': self.play_lights and 'true' or 'false',
            'play_sound': self.play_sound and 'true' or 'false',
            'after_open': self.after_open,
        }
        if self.icon:
            body['icon'] = self.icon
        if self.large_icon:
            body['largeIcon'] = self.large_icon
        if self.img:
            body['img'] = self.img
        if self.sound:
            body['sound'] = self.sound
        if self.builder_id:
            body['builder_id'] = self.builder_id
        if self.url:
            body['url'] = self.url
        if self.activity:
            body['activity'] = self.activity
        if self.custom:
            body['custom'] = self.custom

        result = {
            'display_type': DisplayType.NOTIFICATION,
            'body': body,
        }
        if self.extra:
            result['extra'] = self.extra
        return result


class AndroidPushPolicy:

    def __init__(self, start_time=None, expire_time=None, max_send_num=None,
                 out_biz_no=None):
        """
        :param start_time: datetime
        :param expire_time: datetime
        :param max_send_num: number
        :param out_biz_no: string
        """
        self.start_time = start_time
        self.expire_time = expire_time
        self.max_send_num = max_send_num
        self.out_biz_no = out_biz_no

    @classmethod
    def create(cls, start_time=None, expire_time=None, max_send_num=None,
               out_biz_no=None):

        if start_time and expire_time and expire_time < start_time:
            raise AioUMengPushParamsError('expire time must after start time')

        if max_send_num and max_send_num < 1000:
            raise AioUMengPushParamsError('expire time must >= 1000')

        return cls(start_time=start_time, expire_time=expire_time,
                   max_send_num=max_send_num, out_biz_no=out_biz_no)

    def to_dto(self):
        result = {}
        if self.start_time:
            result['start_time'] = self.start_time.strftime(
                'yyyy-MM-dd HH:mm:ss')
        if self.expire_time:
            result['expire_time'] = self.expire_time.strftime(
                'yyyy-MM-dd HH:mm:ss')
        if self.max_send_num:
            result['max_send_num'] = self.max_send_num
        if self.out_biz_no:
            result['out_biz_no'] = self.out_biz_no
        return result


class AndroidSystemChannel:

    def __init__(self, activity):
        self.activity = activity

    def to_dto(self):
        return {
            'mipush': True,
            'mi_activity': self.activity
        }


class AndroidPush:

    async def single_push_android(self, device_token, msg, description,
                                  policy=None,
                                  system_channel=None):
        """
        :param device_token: string
        :param msg: AndroidPushNotification
        :param policy: AndroidPushPolicy
        :param description: string
        :param system_channel: AndroidSystemChannel
        :return:
        """
        if not self.android_push_config:
            raise AioUMengPushError('android push config not set')

        post_body = {
            'appkey': self.android_push_config.key,
            'timestamp': str(int(datetime.datetime.now().timestamp())),
            'type': PushType.UNI_CAST,
            'device_tokens': device_token,
            'payload': msg.to_dto(),
            'production_mode': self.android_push_config.production_mode,
            'description': description,
        }
        if policy:
            post_body['policy'] = policy.to_dto()

        if system_channel:
            post_body.update(system_channel.to_dto())

        body = json.dumps(post_body, ensure_ascii=False, separators=(',', ':'),
                          sort_keys=True)

        method = 'POST'
        sign = self._get_sign(method, self.GATEWAY, body,
                              self.android_push_config.secret)

        # print(sign)
        result = await self._do_request(method, self.GATEWAY, body,
                                        {'sign': sign})
        return result
