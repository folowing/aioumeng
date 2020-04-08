class AioUMengError(Exception):
    pass


class AioUMengPushError(AioUMengError):
    pass


class AioUMengPushParamsError(AioUMengError):
    pass


class AioUMengPushTimeoutError(AioUMengError):
    pass
