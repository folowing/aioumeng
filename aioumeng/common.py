class PushType:
    # 单播
    UNI_CAST = 'unicast'

    # 列播，要求不超过500个device_token
    LIST_CAST = 'listcast'

    # 文件播，多个device_token可通过文件形式批量发送
    FILE_CAST = 'filecast'

    # 广播
    BROAD_CAST = 'broadcast'

    # 组播，按照filter筛选用户群, 请参照filter参数
    GROUP_CAST = 'groupcast'

    # 通过alias进行推送，包括以下两种case:
    #   - alias: 对单个或者多个alias进行推送
    #   - file_id: 将alias存放到文件后，根据file_id来推送
    CUSTOMIZED_CAST = 'customizedcast'


class DisplayType:
    # 通知消息
    NOTIFICATION = 'notification'

    # 应用内消息
    MESSAGE = 'message'


class AfterOpenType:
    # 打开应用
    GO_APP = 'go_app'

    # 跳转到URL
    GO_URL = 'go_url'

    # 打开特定的activity
    GO_ACTIVITY = 'go_activity'

    # 用户自定义内容
    GO_CUSTOM = 'go_custom'
