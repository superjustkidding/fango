# -*- coding: utf-8 -*-
# @Time    : 2025/9/11 21:55
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from .resources import WeChatPayCreateOrderResource, WeChatPayNotifyResource, WeChatPayQueryResource


def register_payment_routes(api):
    """注册支付路由到主API"""
    api.add_resource(WeChatPayCreateOrderResource, '/pay/wechat/create')  # 创建微信支付订单
    api.add_resource(WeChatPayNotifyResource, '/pay/wechat/notify')  # 微信支付回调
    api.add_resource(WeChatPayQueryResource, '/pay/wechat/query/<string:out_trade_no>')  # 查询支付状态

    # 返回需要保护的端点列表
    return [
        'api.WeChatPayCreateOrderResource',
        'api.WeChatPayQueryResource',
    ]
