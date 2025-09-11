# -*- coding: utf-8 -*-
# @Time    : 2025/8/31 0:01
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : entities.py.py
# @Software: PyCharm

import time
import hashlib
from flask import current_app
from app import db
from app.models.payments import Payment
from app.utils.validation import BusinessValidationError
from app.routes.logger import logger
from lib.ecode import ECode
from app.utils.wechat_utils import WeChatPay


class WeChatPayEntity:
    def __init__(self, current_user=None):
        self.current_user = current_user
        # 初始化微信支付工具
        self.wechat_pay = WeChatPay(
            appid=current_app.config.get('WECHAT_APPID'),
            mch_id=current_app.config.get('WECHAT_MCH_ID'),
            api_key=current_app.config.get('WECHAT_API_KEY'),
            sandbox=current_app.config.get('WECHAT_SANDBOX', True)
        )

    def create_order(self, data):
        """创建微信支付订单"""
        try:
            # 生成商户订单号（如果未提供）
            out_trade_no = data.get('out_trade_no') or self._generate_out_trade_no()

            # 创建本地支付记录
            payment_order = Payment(
                user_id=self.current_user.id if self.current_user else None,
                out_trade_no=out_trade_no,
                total_fee=data['total_fee'],
                body=data['body'],
                attach=data.get('attach', ''),
                trade_type=data.get('trade_type', 'JSAPI'),
                openid=data.get('openid'),
                status='NOTPAY'  # 未支付
            )
            db.session.add(payment_order)
            db.session.commit()

            # 调用微信支付统一下单接口
            result = self.wechat_pay.create_unified_order(
                out_trade_no=out_trade_no,
                total_fee=data['total_fee'],
                body=data['body'],
                spbill_create_ip=data.get('spbill_create_ip', '127.0.0.1'),
                notify_url=current_app.config.get('WECHAT_NOTIFY_URL'),
                trade_type=data.get('trade_type', 'JSAPI'),
                openid=data.get('openid')
            )

            if result.get('return_code') != 'SUCCESS':
                logger.error(f"微信支付下单失败: {result.get('return_msg')}")
                raise BusinessValidationError(f"微信支付下单失败: {result.get('return_msg')}", ECode.ERROR)

            if result.get('result_code') != 'SUCCESS':
                logger.error(f"微信支付业务失败: {result.get('err_code_des')}")
                raise BusinessValidationError(f"微信支付业务失败: {result.get('err_code_des')}", ECode.ERROR)

            # 更新预支付ID
            payment_order.prepay_id = result.get('prepay_id')
            db.session.commit()

            # 生成前端支付参数
            pay_params = self._generate_pay_params(result, data.get('trade_type', 'JSAPI'))

            return {
                'payment_id': payment_order.id,
                'out_trade_no': out_trade_no,
                'pay_params': pay_params
            }, ECode.SUCC

        except Exception as e:
            db.session.rollback()
            logger.error(f"创建支付订单失败: {str(e)}")
            raise BusinessValidationError(f"创建支付订单失败: {str(e)}", ECode.ERROR)

    def handle_notify(self, xml_data):
        """处理微信支付回调"""
        try:
            # 解析XML数据
            notify_data = self.wechat_pay.xml_to_dict(xml_data)

            # 验证签名
            if not self.wechat_pay.verify_sign(notify_data):
                logger.error("微信支付回调签名验证失败")
                return {'return_code': 'FAIL', 'return_msg': '签名失败'}

            # 获取商户订单号
            out_trade_no = notify_data.get('out_trade_no')
            if not out_trade_no:
                logger.error("微信支付回调缺少商户订单号")
                return {'return_code': 'FAIL', 'return_msg': '参数错误'}

            # 查询支付订单
            payment_order = Payment.query.filter_by(out_trade_no=out_trade_no).first()
            if not payment_order:
                logger.error(f"支付订单不存在: {out_trade_no}")
                return {'return_code': 'FAIL', 'return_msg': '订单不存在'}

            # 更新订单状态
            if notify_data.get('return_code') == 'SUCCESS' and notify_data.get('result_code') == 'SUCCESS':
                payment_order.status = 'SUCCESS'
                payment_order.transaction_id = notify_data.get('transaction_id')
                payment_order.time_end = notify_data.get('time_end')
                payment_order.bank_type = notify_data.get('bank_type')
                payment_order.cash_fee = notify_data.get('cash_fee')

                # 这里可以添加业务逻辑，例如更新订单状态、发放商品等
                logger.info(f"支付成功: {out_trade_no}, 金额: {notify_data.get('total_fee')}")
            else:
                payment_order.status = 'FAIL'
                payment_order.err_code = notify_data.get('err_code')
                payment_order.err_code_des = notify_data.get('err_code_des')
                logger.error(f"支付失败: {out_trade_no}, 错误: {notify_data.get('err_code_des')}")

            db.session.commit()

            return {'return_code': 'SUCCESS', 'return_msg': 'OK'}

        except Exception as e:
            db.session.rollback()
            logger.error(f"处理支付回调失败: {str(e)}")
            return {'return_code': 'FAIL', 'return_msg': '处理失败'}

    def query_order(self, out_trade_no):
        """查询支付订单状态"""
        try:
            payment_order = Payment.query.filter_by(out_trade_no=out_trade_no).first()
            if not payment_order:
                raise BusinessValidationError("支付订单不存在", ECode.NOTFOUND)

            # 检查当前用户是否有权限查看此订单
            if self.current_user and payment_order.user_id != self.current_user.id and not self.current_user.is_admin:
                raise BusinessValidationError("无权查看此订单", ECode.FORBID)

            return payment_order.to_dict(), ECode.SUCC

        except Exception as e:
            logger.error(f"查询支付订单失败: {str(e)}")
            raise BusinessValidationError(f"查询支付订单失败: {str(e)}", ECode.ERROR)

    def _generate_out_trade_no(self):
        """生成商户订单号"""
        timestamp = int(time.time())
        random_str = ''.join([str(i) for i in range(10)]).zfill(6)
        return f"{timestamp}{random_str}"

    def _generate_pay_params(self, result, trade_type):
        """生成前端支付参数"""
        if trade_type == 'JSAPI':
            # JSAPI支付参数
            prepay_id = result.get('prepay_id')
            timestamp = str(int(time.time()))
            nonce_str = self.wechat_pay.generate_nonce_str()
            package = f"prepay_id={prepay_id}"

            # 生成签名
            sign_dict = {
                'appId': current_app.config.get('WECHAT_APPID'),
                'timeStamp': timestamp,
                'nonceStr': nonce_str,
                'package': package,
                'signType': 'MD5'
            }
            pay_sign = self.wechat_pay.generate_sign(sign_dict)

            return {
                'appId': current_app.config.get('WECHAT_APPID'),
                'timeStamp': timestamp,
                'nonceStr': nonce_str,
                'package': package,
                'signType': 'MD5',
                'paySign': pay_sign
            }
        else:
            # 其他支付方式返回原始结果
            return result

