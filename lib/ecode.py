# -*- coding: utf-8 -*-
# @Time    : 2025/8/7 12:29
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : ecode.py
# @Software: PyCharm
"""
全局配置业务错误码
"""
from .enum import Enum, EnumMem


class ECode(Enum):
    """
    错误码-中文
    """
    SUCC = EnumMem(200, ("成功", "SUCC"))
    ERROR = EnumMem(400, ("页面去火星了", "NOT FOUND"))
    AUTH = EnumMem(401, ("鉴权失败", "Authentication Failed"))
    FORBID = EnumMem(403, ("访问禁止", "Access Forbidden"))
    NOTFOUND = EnumMem(404, ("资源不存在", "Resource Does Not Exist"))
    PARAM = EnumMem(406, ("参数错误", "Parameter Error"))
    INTER = EnumMem(500, ("内部错误", "Internal Error"))
    EXTERNAL = EnumMem(503, ("外部错误", "External Error"))
    RUNTIME = EnumMem(504, ("运行时错误", "Runtime Error"))
    NOTFILE = EnumMem(600, ("文件不存在", "File Does Not Exist"))
    UPLOAD = EnumMem(601, ("文件上传异常", "File Upload Exception"))
    REFRESH = EnumMem(602, ("需要刷新", "Need Refresh"))

    # 自定义状态码
    NotBillError = EnumMem(24007, ("账单不存在", "bill does not exist"))
    RemovedBillError = EnumMem(24008,
        (
            "该账单已支付，无法移除",
            "This bill has already been paid and cannot be removed",
        ),
    )
    InvoiceError = EnumMem(
        24009,
        (
            "该账单已创建发票，无需重复创建",
            "The bill has already created an invoice, no need to create it again",
        ),
    )
    NotPaymentError = EnumMem(
        24010, ("付款记录不存在", "Payment record does not exist")
    )
    PaymentIntentError = EnumMem(
        24011, ("创建stripe付款记录失败", "Create stripe payment record failed")
    )
    NotInvoiceError = EnumMem(24012, ("发票不存在", "Invoice does not exist"))
    WechatNotifyError = EnumMem(24013, ("微信回调失败", "Wechat callback failed"))
    WechatConfigNotExist = EnumMem(24014, ("微信配置不存在", "Wechat configuration does not exist"))
    PaymentTypeNotExist = EnumMem(24015, ("支付方式不存在", "Payment method does not exist"))


def init(_ECode=None):
    global ECode
    if _ECode:
        ECode = _ECode
