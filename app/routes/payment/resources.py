# -*- coding: utf-8 -*-
# @Time    : 2025/8/31 0:02
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : resources.py.py
# @Software: PyCharm

from flask_restful import Resource
from flask import request, current_app
from .entities import WeChatPayEntity
from app.schemas.payment.payment_schema import WeChatPayCreateOrderSchema
from app.utils.validation import validate_request
from app.routes.jwt import current_user, user_required
from app.routes.logger import logger


class WeChatPayCreateOrderResource(Resource):
    endpoint = 'api.WeChatPayCreateOrderResource'

    @user_required
    def post(self):
        """创建微信支付订单"""
        data = validate_request(WeChatPayCreateOrderSchema, request.get_json())
        entity = WeChatPayEntity(current_user=current_user)
        return entity.create_order(data)


class WeChatPayNotifyResource(Resource):
    endpoint = 'api.WeChatPayNotifyResource'

    def post(self):
        """微信支付回调通知"""
        # 微信支付回调使用XML格式，不是JSON
        xml_data = request.data.decode('utf-8')
        logger.info(f"收到微信支付回调: {xml_data}")

        entity = WeChatPayEntity()
        result = entity.handle_notify(xml_data)

        # 返回XML格式的响应
        from app.utils.wechat_utils import WeChatPay
        wechat_pay = WeChatPay(
            appid=current_app.config.get('WECHAT_APPID'),
            mch_id=current_app.config.get('WECHAT_MCH_ID'),
            api_key=current_app.config.get('WECHAT_API_KEY'),
            sandbox=current_app.config.get('WECHAT_SANDBOX', True)
        )
        return wechat_pay.dict_to_xml(result), 200, {'Content-Type': 'application/xml'}


class WeChatPayQueryResource(Resource):
    endpoint = 'api.WeChatPayQueryResource'

    @user_required
    def get(self, out_trade_no):
        """查询支付订单状态"""
        entity = WeChatPayEntity(current_user=current_user)
        return entity.query_order(out_trade_no)

