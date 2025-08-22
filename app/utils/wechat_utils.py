# -*- coding: utf-8 -*-
# @Time    : 2025/8/21 12:14
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : wechat_utils.py.py
# @Software: PyCharm


import hashlib
import xml.etree.ElementTree as ET
import requests
import random
import string

# 微信支付的工具类
class WeChatPay:
    def __init__(self, appid, mch_id, api_key, sandbox=False):
        self.appid = appid
        self.mch_id = mch_id
        self.api_key = api_key
        self.sandbox = sandbox

        if sandbox:
            self.unifiedorder_url = 'https://api.mch.weixin.qq.com/sandboxnew/pay/unifiedorder'
            self._get_sandbox_key()
        else:
            self.unifiedorder_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'

    def _get_sandbox_key(self):
        """获取沙箱环境API密钥"""
        try:
            params = {
                'mch_id': self.mch_id,
                'nonce_str': self.generate_nonce_str()
            }
            params['sign'] = self.generate_sign(params)

            xml_data = self.dict_to_xml(params)
            response = requests.post(
                'https://api.mch.weixin.qq.com/sandboxnew/pay/getsignkey',
                data=xml_data,
                headers={'Content-Type': 'application/xml'}
            )

            result = self.xml_to_dict(response.text)
            if result.get('return_code') == 'SUCCESS':
                self.api_key = result.get('sandbox_signkey')
        except Exception as e:
            print(f"获取沙箱密钥失败: {e}")

    def generate_nonce_str(self, length=32):
        """生成随机字符串"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def generate_sign(self, params):
        """生成签名"""
        # 参数按ASCII码排序
        sorted_params = sorted(params.items())
        # 拼接成URL参数形式
        stringA = '&'.join([f"{k}={v}" for k, v in sorted_params if v and k != 'sign'])
        # 拼接API密钥
        stringSignTemp = f"{stringA}&key={self.api_key}"
        # MD5加密并转为大写
        return hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()

    def dict_to_xml(self, params):
        """字典转XML"""
        xml = ["<xml>"]
        for k, v in params.items():
            if v is not None:
                xml.append(f"<{k}><![CDATA[{v}]]></{k}>")
            else:
                xml.append(f"<{k}></{k}>")
        xml.append("</xml>")
        return ''.join(xml)

    def xml_to_dict(self, xml_str):
        """XML转字典"""
        result = {}
        root = ET.fromstring(xml_str)
        for child in root:
            result[child.tag] = child.text
        return result

    def create_unified_order(self, out_trade_no, total_fee, body, spbill_create_ip, notify_url, trade_type='JSAPI',
                             openid=None):
        """创建统一下单"""
        params = {
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': self.generate_nonce_str(),
            'body': body,
            'out_trade_no': out_trade_no,
            'total_fee': total_fee,
            'spbill_create_ip': spbill_create_ip,
            'notify_url': notify_url,
            'trade_type': trade_type,
            'openid': openid
        }

        # 移除空值
        params = {k: v for k, v in params.items() if v is not None}

        # 生成签名
        params['sign'] = self.generate_sign(params)

        # 转换为XML
        xml_data = self.dict_to_xml(params)

        # 发送请求
        response = requests.post(self.unifiedorder_url, data=xml_data, headers={'Content-Type': 'application/xml'})

        # 解析响应
        result = self.xml_to_dict(response.text)

        return result

    def verify_sign(self, params):
        """验证签名"""
        if 'sign' not in params:
            return False

        sign = params.pop('sign')
        calculated_sign = self.generate_sign(params)
        return sign == calculated_sign

