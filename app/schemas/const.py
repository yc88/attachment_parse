from enum import Enum, auto

Allowed_Extensions = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.csv',
                      '.ppt', '.pptx', '.png', '.jpg', '.jpeg', '.pdf', '.html', '.htm', '.eml', '.xml']


class MyErrorCode(Enum):
    OK = 0  # 操作成功
    Canceled = 1  # 已取消
    Unknown = 2  # 未知错误
    InvalidArgument = 3  # 参数非法
    DeadlineExceeded = 4  # 超时
    NotFound = 5  # 找不到资源
    AlreadyExists = 6  # 已存在
    PermissionDenied = 7  # 无权限
    ResourceExhausted = 8  # 资源不足
    FailedPrecondition = 9  # 前提条件不正确
    Aborted = 10  # 终止
    OutOfRange = 11  # 超出范围
    Unimplemented = 12  # 未实现
    Internal = 13  # 内部错误
    Unavailable = 14  # 不可用
    DataLoss = 15  # 数据丢失
    Unauthenticated = 16  # 没有鉴权
    NotYetDeveloped = 17  # 暂未开发
    EsConnectUnknownFail = 18  # 请选择Es连接
    ArgumentNotEmpty = 19  # 参数不能为空
    UserAccountDisable = 20  # 用户被禁用
    AccountNotLoggedIn = 21  # 账号未登录


# 定义字典常量
My_Error_Msg = {
    MyErrorCode.OK.value: "操作成功",
    MyErrorCode.Canceled.value: "已取消",
    MyErrorCode.Unknown.value: "未知错误",
    MyErrorCode.InvalidArgument.value: "参数非法",
    MyErrorCode.DeadlineExceeded.value: "超时",
    MyErrorCode.NotFound.value: "找不到资源",
    MyErrorCode.AlreadyExists.value: "已存在",
    MyErrorCode.PermissionDenied.value: "无权限",
    MyErrorCode.ResourceExhausted.value: "资源不足",
    MyErrorCode.FailedPrecondition.value: "前提条件不正确",
    MyErrorCode.Aborted.value: "终止",
    MyErrorCode.OutOfRange.value: "超出范围",
    MyErrorCode.Unimplemented.value: "未实现",
    MyErrorCode.Internal.value: "内部错误",
    MyErrorCode.Unavailable.value: "不可用",
    MyErrorCode.DataLoss.value: "数据丢失",
    MyErrorCode.Unauthenticated.value: "没有鉴权",
    MyErrorCode.NotYetDeveloped.value: "暂未开发",
    MyErrorCode.EsConnectUnknownFail.value: "请选择Es连接",
    MyErrorCode.ArgumentNotEmpty.value: "参数不能为空",
    MyErrorCode.UserAccountDisable.value: "用户被禁用",
    MyErrorCode.AccountNotLoggedIn.value: "账号未登录",
}


class MyErrors(Exception):
    def __init__(self, err, code):
        self.err = err
        self.code = code

    def __str__(self):
        return self.err


def New(str, code):
    return MyErrors(str, code)


def GetErrMsg(code):
    return My_Error_Msg[code]


def CheckedError(err):
    if isinstance(err, MyErrors):
        return True, err.code, GetErrMsg(err.code), err
    return False, MyErrorCode.Internal, GetErrMsg(MyErrorCode.Internal), err


def NewError(string2):
    return Exception(string2)


class HttpStatusCode:
    HTTP_100_CONTINUE = 100
    HTTP_101_SWITCHING_PROTOCOLS = 101
    HTTP_102_PROCESSING = 102
    HTTP_103_EARLY_HINTS = 103
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_202_ACCEPTED = 202
    HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203
    HTTP_204_NO_CONTENT = 204
    HTTP_205_RESET_CONTENT = 205
    HTTP_206_PARTIAL_CONTENT = 206
    HTTP_207_MULTI_STATUS = 207
    HTTP_208_ALREADY_REPORTED = 208
    HTTP_226_IM_USED = 226
    HTTP_300_MULTIPLE_CHOICES = 300
    HTTP_301_MOVED_PERMANENTLY = 301
    HTTP_302_FOUND = 302
    HTTP_303_SEE_OTHER = 303
    HTTP_304_NOT_MODIFIED = 304
    HTTP_305_USE_PROXY = 305
    HTTP_306_RESERVED = 306
    HTTP_307_TEMPORARY_REDIRECT = 307
    HTTP_308_PERMANENT_REDIRECT = 308
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_402_PAYMENT_REQUIRED = 402
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_406_NOT_ACCEPTABLE = 406
    HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
    HTTP_408_REQUEST_TIMEOUT = 408
    HTTP_409_CONFLICT = 409
    HTTP_410_GONE = 410
    HTTP_411_LENGTH_REQUIRED = 411
    HTTP_412_PRECONDITION_FAILED = 412
    HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
    HTTP_414_REQUEST_URI_TOO_LONG = 414
    HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
    HTTP_417_EXPECTATION_FAILED = 417
    HTTP_418_IM_A_TEAPOT = 418
    HTTP_421_MISDIRECTED_REQUEST = 421
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_423_LOCKED = 423
    HTTP_424_FAILED_DEPENDENCY = 424
    HTTP_425_TOO_EARLY = 425
    HTTP_426_UPGRADE_REQUIRED = 426
    HTTP_428_PRECONDITION_REQUIRED = 428
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS = 451
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_501_NOT_IMPLEMENTED = 501
    HTTP_502_BAD_GATEWAY = 502
    HTTP_503_SERVICE_UNAVAILABLE = 503
    HTTP_504_GATEWAY_TIMEOUT = 504
    HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
    HTTP_506_VARIANT_ALSO_NEGOTIATES = 506
    HTTP_507_INSUFFICIENT_STORAGE = 507
    HTTP_508_LOOP_DETECTED = 508
    HTTP_510_NOT_EXTENDED = 510
    HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511
