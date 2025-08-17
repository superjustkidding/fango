# -*- coding:utf-8 -*-
from flask import jsonify
from functools import wraps
from traceback import format_exc
# from wechatpy import WeChatOAuthException
from .exception import BusinessError
from marshmallow.validate import ValidationError
from extensions.flask_auth import JWTError


def response_json():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                ret = fn(*args, **kwargs)
                return jsonify({'status': 1, 'data': ret})
            except ValidationError as e:
                return jsonify({'status': 0, 'errCode': 60003, 'errMsg': e.messages})
            except BusinessError as e:
                return jsonify({'status': 0, 'errCode': e.status_code, 'errMsg': e.description})
            except JWTError as e:
                return jsonify({'status': 0, 'errCode': e.status_code, 'errMsg': e.description})
            # except WeChatOAuthException as e:
            #     return {'status': 0, 'errCode': e.errcode, 'errMsg': e.errmsg}
            except Exception as e:
                print(e)
            return jsonify({'status': 0, 'errCode': 500, 'errMsg': 'Internal Server Error!'})

        return decorator

    return wrapper


def _log_it(logger, _caller_name, _caller_exception, *args, **kwargs):
    if _caller_exception:
        msg = ' {0} eeeee \n Type: {1} {2} \n Msg: {3}'.format(_caller_name, type(_caller_exception), _caller_exception,
                                                               format_exc())
    else:
        if len(args) > 1:
            msg = ' {0} ***** \n args: {1} \nkwargs: {2}'.format(_caller_name, args[1:], str(kwargs))
        else:
            msg = ' {0} ***** \nkwargs: {1}'.format(_caller_name, str(kwargs))
    if logger:
        if _caller_exception:
            logger.error(msg)
        else:
            logger.info(msg)
    else:
        print(msg)


def api(app_name='mobile', api_name='', logger=None):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            called_name = '{0}.{1}.{2}'.format(app_name, api_name, fn.__name__)
            try:
                _log_it(logger, called_name, None, *args, **kwargs)
                return fn(*args, **kwargs)
            except Exception as e:
                _log_it(logger, called_name, e, *args, **kwargs)
                raise e
        return decorator
    return wrapper
