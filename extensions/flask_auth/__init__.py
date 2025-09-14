# -*- coding:utf-8 -*-
"""
    Author: Kimi Shi Xi'an HackTech Co,Ltd
"""
__version__ = '0.0.1'

import logging
import flask_jwt_extended as pyjwt
from datetime import datetime, timedelta
from functools import wraps

from flask import request, jsonify, _request_ctx_stack
from werkzeug.local import LocalProxy

logger = logging.getLogger(__name__)

current_user = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_user', None))


class JWTError(Exception):
    def __init__(self, error, description, status_code=401):
        self.error = error
        self.description = description
        self.status_code = status_code

    def __repr__(self):
        return 'JWTError: %s' % self.error

    def __str__(self):
        return '%s. %s' % (self.error, self.description)


class JWTAuth:
    def __init__(self, get_identity_cb=None, algorithm='HS256', secret='secret', leeway_seconds=10, exp_seconds=300,
                 nbf_seconds=0):
        self.algorithm = algorithm
        self._secret = secret
        self._leeway = timedelta(seconds=leeway_seconds)
        self._exp = timedelta(seconds=exp_seconds)
        self._nbf = timedelta(seconds=nbf_seconds)
        self._options = {'verify_' + claim: True for claim in self.JWT_VERIFY_CLAIMS}
        self._options.update({'require_' + claim: True for claim in self.JWT_VERIFY_CLAIMS})
        self._auth_header_prefix = 'JWT'
        self._get_identity_cb = get_identity_cb

    def __call__(self, get_identity_cb=None):
        self._get_identity_cb = get_identity_cb

    JWT_VERIFY_CLAIMS = ['signature', 'exp', 'nbf', 'iat']
    JWT_REQUIRED_CLAIMS = ['exp', 'iat', 'nbf']

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, secret):
        self._secret = secret

    @property
    def leeway(self):
        return self._leeway

    @leeway.setter
    def leeway(self, leeway_seconds):
        self._leeway = timedelta(seconds=leeway_seconds)

    @property
    def exp(self):
        return self._exp

    @exp.setter
    def exp(self, exp_seconds):
        self._exp = timedelta(seconds=exp_seconds)

    @property
    def nbf(self):
        return self._nbf

    @nbf.setter
    def nbf(self, nbf_seconds):
        self._nbf = timedelta(seconds=nbf_seconds)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    @property
    def auth_header_prefix(self):
        return self._auth_header_prefix.lower()

    @property
    def get_identity_cb(self):
        return self._get_identity_cb

    @get_identity_cb.setter
    def get_identity_cb(self, cb):
        self._get_identity_cb = cb

    def _default_payload(self):
        iat = datetime.utcnow()
        exp = iat + self.exp
        nbf = iat + self.nbf
        return {'exp': exp, 'iat': iat, 'nbf': nbf}

    def _merge_payload(self, user_payload):
        if not isinstance(user_payload, dict):
            raise JWTError(error='Type error', description='Payload is not dict object', status_code=400)
        payload = user_payload.copy()
        payload.update(self._default_payload())
        return payload

    def encode(self, user_payload):
        payload = self._merge_payload(user_payload)
        return pyjwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode(self, jwt_token):
        return pyjwt.decode(jwt_token, self.secret, algorithms=self.algorithm,
                            options=self.options, leeway=self.leeway)

    def _parse_request_header(self):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            raise JWTError('Invalid JWT header', 'Authorization field not found in http header')

        parts = auth_header.split(' ')

        if parts[0].lower() != self.auth_header_prefix:
            raise JWTError('Invalid JWT header', 'Unsupported authorization type')
        if len(parts) == 1:
            raise JWTError('Invalid JWT header', 'Token missing')
        if len(parts) > 2:
            raise JWTError('Invalid JWT header', 'Token contains spaces')

        return parts[1]

    def _jwt_required(self):
        if request.method == 'OPTIONS':
            return
        jwt_token = self._parse_request_header()

        try:
            payload = self.decode(jwt_token)
            _request_ctx_stack.top.current_user = identity = self.get_identity_cb(payload)
        except pyjwt.InvalidTokenError as e:
            raise JWTError('Invalid JWT token.txt', str(e), status_code=403)
        if identity is None:
            raise JWTError('Invalid JWT', 'User not exist', status_code=403)

    def jwt_required(self):
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                try:
                    self._jwt_required()
                    return fn(*args, **kwargs)
                except JWTError as e:
                    return jsonify({'status': 0, 'errCode': e.status_code, 'errMsg': str(e)})
                except Exception as e:
                    print(e)
                    return jsonify({'status': 0, 'errCode': 502, 'errMsg': 'Internal Server Error!'})

            return decorator

        return wrapper

    @property
    def visitor(self):
        """
        获取访问者
        :return:
        """
        jwt_token = self._parse_request_header()
        try:
            payload = self.decode(jwt_token)
            return self.get_identity_cb(payload)
        except pyjwt.InvalidTokenError as e:
            return None
